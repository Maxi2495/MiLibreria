import React, { useState } from 'react';

const DEFAULT_COVER = 'https://images.placeholders.dev/?width=300&height=450&text=Sin+Portada&theme=neutral';

interface Props extends React.ImgHTMLAttributes<HTMLImageElement> {
  fallbackSrc?: string;
}

export const FallbackImage: React.FC<Props> = ({ src, alt, fallbackSrc = DEFAULT_COVER, className, ...props }) => {
  const [imgSrc, setImgSrc] = useState<string>(src || fallbackSrc);

  return (
    <img
      {...props}
      src={imgSrc}
      alt={alt}
      className={className}
      onError={() => setImgSrc(fallbackSrc)}
      loading="lazy"
    />
  );
};