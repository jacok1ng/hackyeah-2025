import Svg, { Path } from "react-native-svg";

export const StatusIcon = (props: any) => {
  return (
    <Svg width="21" height="22" viewBox="0 0 21 22" fill="none" {...props}>
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M10.5 0.5C7.6493 0.5 5.01905 1.64345 3.08495 3.5849L1.05005 1.55V7.85H7.35005L4.5686 5.06855C6.11525 3.51455 8.21945 2.6 10.5 2.6C15.1316 2.6 18.9 6.36845 18.9 11H21C21 5.2103 16.2898 0.5 10.5 0.5Z"
        fill="currentColor"
      />
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M19.95 14.15H13.65L16.4315 16.9314C14.8848 18.4854 12.7817 19.4 10.5 19.4C5.86845 19.4 2.1 15.6315 2.1 11H0C0 16.7897 4.7103 21.5 10.5 21.5C13.3518 21.5 15.9821 20.3565 17.9151 18.4151L19.95 20.45V14.15Z"
        fill="currentColor"
      />
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M11.55 12.05H9.44995V5.75H11.55V12.05Z"
        fill="currentColor"
      />
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M11.8125 15.2C11.8125 15.9245 11.2245 16.5125 10.5 16.5125C9.7755 16.5125 9.1875 15.9245 9.1875 15.2C9.1875 14.4755 9.7755 13.8875 10.5 13.8875C11.2245 13.8875 11.8125 14.4755 11.8125 15.2Z"
        fill="currentColor"
      />
    </Svg>
  );
};
