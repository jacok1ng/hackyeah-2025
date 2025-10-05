import Svg, { Path } from "react-native-svg";

export const ObstacleIcon = (props: any) => {
  return (
    <Svg width="40" height="40" viewBox="0 0 40 40" fill="none" {...props}>
      <Path
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M25.6001 6.35019H17.8001L13.9001 21.9502H21.7001L25.6001 6.35019Z"
        fill="currentColor"
      />
      <Path
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M37.3 6.35H35.35V0.5H31.45V6.35L27.55 21.95H31.45V29.75H8.05V21.95L11.95 6.35H8.05V0.5H4.15V6.35H2.2C1.1236 6.35 0.25 7.2236 0.25 8.3V20C0.25 21.0764 1.1236 21.95 2.2 21.95H4.15V39.5H8.05V33.65H31.45V39.5H35.35V21.95H37.3C38.3764 21.95 39.25 21.0764 39.25 20V8.3C39.25 7.2236 38.3764 6.35 37.3 6.35Z"
        fill="currentColor"
      />
    </Svg>
  );
};
