import Svg, { Path } from "react-native-svg";

export const MapMarkerIcon = (props: any) => {
  return (
    <Svg width="14" height="20" viewBox="0 0 14 20" fill="none" {...props}>
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M7 9.5C5.62 9.5 4.5 8.381 4.5 7C4.5 5.619 5.62 4.5 7 4.5C8.381 4.5 9.5 5.619 9.5 7C9.5 8.381 8.381 9.5 7 9.5ZM7 0C3.134 0 0 3.134 0 7C0 12 7 20 7 20C7 20 14 12 14 7C14 3.134 10.866 0 7 0Z"
        fill="currentColor"
      />
    </Svg>
  );
};
