import Svg, { Path } from "react-native-svg";

export const BackArrowIcon = (props: any) => {
  return (
    <Svg width="10" height="18" viewBox="0 0 10 18" fill="none" {...props}>
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M0 9C0 8.66774 0.127193 8.33547 0.380283 8.08238L8.16767 0.294998L10.0029 2.13023L3.13312 9L10.0029 15.8698L8.16767 17.705L0.380283 9.91761C0.127193 9.66452 0 9.33226 0 9Z"
        fill="currentColor"
      />
    </Svg>
  );
};
