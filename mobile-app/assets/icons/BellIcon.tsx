import Svg, { Path } from "react-native-svg";

export const BellIcon = (props: any) => {
  return (
    <Svg width="20" height="20" viewBox="0 0 20 20" fill="none" {...props}>
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M16.6667 12.2222V6.66667C16.6667 2.98444 13.6833 0 10 0C6.31667 0 3.33333 2.98444 3.33333 6.66667V12.2222C3.33333 14.0633 1.84 15.5556 0 15.5556V16.6667H20V15.5556C18.16 15.5556 16.6667 14.0633 16.6667 12.2222Z"
        fill="#FBC535"
      />
      <Path
        fill-rule="evenodd"
        clipRule="evenodd"
        d="M6.17188 17.7775C6.94188 19.0998 8.35965 19.9998 9.99965 19.9998C11.6408 19.9998 13.0574 19.0998 13.8285 17.7775H6.17188Z"
        fill="#FBC535"
      />
    </Svg>
  );
};
