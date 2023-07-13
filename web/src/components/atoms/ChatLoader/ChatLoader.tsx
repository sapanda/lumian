import { useState, useEffect } from "react";
export default function ChatLoader() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((index) => (index + 1) % 3);
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <svg
      width="90"
      height="47"
      viewBox="0 0 90 47"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g filter="url(#filter0_d_1694_2935)">
        <g clipPath="url(#clip0_1694_2935)">
          <path
            d="M6 16C6 10.4772 10.4772 6 16 6H74C79.5228 6 84 10.4772 84 16V31C84 36.5228 79.5228 41 74 41H16C10.4772 41 6 36.5228 6 31V16Z"
            fill="white"
          />
          <circle
            cx="31"
            cy="23.5"
            r="4"
            transform="rotate(180 31 23.5)"
            fill={index === 0 ? "#2D2D2D" : "#D9D9D9"}
          />
          <circle
            cx="45"
            cy="23.5"
            r="4"
            transform="rotate(180 45 23.5)"
            fill={index === 1 ? "#2D2D2D" : "#D9D9D9"}
          />
          <circle
            cx="59"
            cy="23.5"
            r="4"
            transform="rotate(180 59 23.5)"
            fill={index === 2 ? "#2D2D2D" : "#D9D9D9"}
          />
        </g>
      </g>
      <defs>
        <filter
          id="filter0_d_1694_2935"
          x="0"
          y="0"
          width="90"
          height="47"
          filterUnits="userSpaceOnUse"
          colorInterpolationFilters="sRGB"
        >
          <feFlood floodOpacity="0" result="BackgroundImageFix" />
          <feColorMatrix
            in="SourceAlpha"
            type="matrix"
            values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
            result="hardAlpha"
          />
          <feOffset />
          <feGaussianBlur stdDeviation="3" />
          <feComposite in2="hardAlpha" operator="out" />
          <feColorMatrix
            type="matrix"
            values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0"
          />
          <feBlend
            mode="normal"
            in2="BackgroundImageFix"
            result="effect1_dropShadow_1694_2935"
          />
          <feBlend
            mode="normal"
            in="SourceGraphic"
            in2="effect1_dropShadow_1694_2935"
            result="shape"
          />
        </filter>
        <clipPath id="clip0_1694_2935">
          <path
            d="M6 16C6 10.4772 10.4772 6 16 6H74C79.5228 6 84 10.4772 84 16V31C84 36.5228 79.5228 41 74 41H16C10.4772 41 6 36.5228 6 31V16Z"
            fill="white"
          />
        </clipPath>
      </defs>
    </svg>
  );
}
