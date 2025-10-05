import Svg, { Path } from "react-native-svg";

export const HearthIcon = (props: any) => {
  return (
    <Svg width="24" height="20" viewBox="0 0 24 20" fill="none" {...props}>
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M17 0C15.0075 0 13.1613 1.04625 12 2.6C10.8387 1.04625 8.9925 0 7 0C3.55375 0 0.75 2.80375 0.75 6.25C0.75 13.1138 10.905 19.54 11.3375 19.81C11.54 19.9362 11.77 20 12 20C12.23 20 12.46 19.9362 12.6625 19.81C13.095 19.54 23.25 13.1138 23.25 6.25C23.25 2.80375 20.4463 0 17 0Z"
        fill="currentColor"
      />
    </Svg>
  );
};
