import os
import re
from typing import Any, Dict, Optional
import httpx
from fastapi import HTTPException, status
from app.schemas.catalogo import LibroISBNResponse

DEFAULT_COVER_FALLBACK = "https://images.placeholders.dev/?width=300&height=450&text=Sin+Portada&theme=neutral"
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_API_URL = "https://openlibrary.org/api/books"

# Permite configurar una API Key de Google Cloud en el .env si se dispone de una
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


class ISBNService:
    @staticmethod
    def sanitizar_isbn(isbn_raw: str) -> str:
        """
        Remueve guiones y espacios; valida estructura de ISBN-10 o ISBN-13.
        """
        isbn_limpio = re.sub(r"[-\s]", "", isbn_raw).strip().upper()
        if not re.fullmatch(r"(\d{9}[\dX]|\d{13})", isbn_limpio):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El formato del ISBN '{isbn_raw}' es inválido. Debe poseer 10 o 13 caracteres alfanuméricos válidos.",
            )
        return isbn_limpio

    @staticmethod
    def _normalizar_portada_url(url: Optional[str]) -> str:
        if not url:
            return DEFAULT_COVER_FALLBACK
        if url.startswith("http://"):
            return "https://" + url[7:]
        return url

    async def _consultar_google_books(self, client: httpx.AsyncClient, isbn: str) -> Optional[LibroISBNResponse]:
        """Consulta Google Books API."""
        params = {"q": f"isbn:{isbn}"}
        if GOOGLE_BOOKS_API_KEY:
            params["key"] = GOOGLE_BOOKS_API_KEY

        headers = {"User-Agent": "BookNest-App/1.0 (academic-project)"}

        try:
            response = await client.get(GOOGLE_BOOKS_API_URL, params=params, headers=headers)
            if response.status_code == 429 or response.status_code >= 500:
                # Quota excedida o servidor caído -> disparar fallback
                return None
            if response.status_code != 200:
                return None

            data = response.json()
            if data.get("totalItems", 0) == 0 or "items" not in data:
                return None

            volume_info = data["items"][0].get("volumeInfo", {})
            image_links = volume_info.get("imageLinks", {})
            raw_cover = (
                image_links.get("thumbnail")
                or image_links.get("smallThumbnail")
                or image_links.get("medium")
                or image_links.get("large")
            )

            return LibroISBNResponse(
                isbn=isbn,
                titulo=volume_info.get("title", "Sin título registrado"),
                autores=volume_info.get("authors", []),
                editorial=volume_info.get("publisher"),
                fecha_publicacion=volume_info.get("publishedDate"),
                sinopsis=volume_info.get("description"),
                generos=volume_info.get("categories", []),
                portada_url=self._normalizar_portada_url(raw_cover),
            )
        except (httpx.TimeoutException, httpx.RequestError):
            return None

    async def _consultar_open_library(self, client: httpx.AsyncClient, isbn: str) -> Optional[LibroISBNResponse]:
        """Consulta Open Library API como proveedor de respaldo."""
        bibkey = f"ISBN:{isbn}"
        params = {
            "bibkeys": bibkey,
            "format": "json",
            "jscmd": "data"
        }
        headers = {"User-Agent": "BookNest/1.0 (trabajofinal@utn.edu.ar)"}

        try:
            response = await client.get(OPEN_LIBRARY_API_URL, params=params, headers=headers)
            if response.status_code != 200:
                return None

            data = response.json()
            if bibkey not in data:
                return None

            book_info = data[bibkey]

            # Autores
            autores = [a.get("name") for a in book_info.get("authors", []) if "name" in a]
            
            # Editorial (primera disponible)
            editoriales = book_info.get("publishers", [])
            editorial = editoriales[0].get("name") if editoriales else None

            # Géneros / subjects
            generos = [s.get("name") for s in book_info.get("subjects", []) if "name" in s][:5]

            # Portadas
            covers = book_info.get("cover", {})
            raw_cover = covers.get("large") or covers.get("medium") or covers.get("small")
            if not raw_cover:
                raw_cover = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"

            # Sinopsis (en Open Library puede venir en notes o description)
            sinopsis = book_info.get("notes")
            if not sinopsis:
                desc = book_info.get("description")
                if isinstance(desc, dict):
                    sinopsis = desc.get("value")
                elif isinstance(desc, str):
                    sinopsis = desc

            return LibroISBNResponse(
                isbn=isbn,
                titulo=book_info.get("title", "Sin título registrado"),
                autores=autores,
                editorial=editorial,
                fecha_publicacion=book_info.get("publish_date"),
                sinopsis=sinopsis,
                generos=generos,
                portada_url=self._normalizar_portada_url(raw_cover),
            )
        except (httpx.TimeoutException, httpx.RequestError):
            return None

    async def consultar_por_isbn(self, isbn_raw: str) -> LibroISBNResponse:
        isbn = self.sanitizar_isbn(isbn_raw)
        timeout_config = httpx.Timeout(timeout=6.0, connect=3.0)

        async with httpx.AsyncClient(timeout=timeout_config) as client:
            # 1. Intento primario: Google Books
            libro = await self._consultar_google_books(client, isbn)

            # 2. Respaldo por contingencia: Open Library
            if not libro:
                libro = await self._consultar_open_library(client, isbn)

        # 3. Si ninguno de los dos proveedores cuenta con el registro
        if not libro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró información bibliográfica para el ISBN {isbn}. Puede ingresarse de forma manual.",
            )

        return libro


isbn_service = ISBNService()