import Svg, { Path, Rect } from "react-native-svg";

export const CheckmarkIcon = (props: any) => {
  return (
    <Svg width="28" height="28" viewBox="0 0 28 28" fill="none" {...props}>
      <Rect width="28" height="28" rx="14" fill="white" />
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M12.543 19.909L7.15141 14.5174L9.20797 12.4608L12.543 15.7958L18.7868 9.55197L20.8434 11.6085L12.543 19.909ZM14 2C7.3832 2 2 7.3832 2 14C2 20.6168 7.3832 26 14 26C20.6168 26 26 20.6168 26 14C26 7.3832 20.6168 2 14 2Z"
        fill="#23D48B"
      />
    </Svg>
  );
};
