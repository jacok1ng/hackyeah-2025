import Svg, { Path } from "react-native-svg";

export const AvatarIcon = (props: any) => {
  return (
    <Svg width="22" height="22" viewBox="0 0 22 22" fill="none" {...props}>
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M11 11C13.8954 11 16.25 8.64538 16.25 5.75C16.25 2.85462 13.8954 0.5 11 0.5C8.10462 0.5 5.75 2.85462 5.75 5.75C5.75 8.64538 8.10462 11 11 11Z"
        fill="currentColor"
      />
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M11 12.3125C4.81812 12.3125 0.5 15.5504 0.5 20.1875V21.5H21.5V20.1875C21.5 15.5504 17.1819 12.3125 11 12.3125Z"
        fill="currentColor"
      />
    </Svg>
  );
};
