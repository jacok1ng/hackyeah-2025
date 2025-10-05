import Svg, { Path } from "react-native-svg";

export const ClockIcon = (props: any) => {
  return (
    <Svg width="15" height="16" viewBox="0 0 15 16" fill="none" {...props}>
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M9.41079 11.0893L6.91079 8.58927C6.75413 8.43343 6.66663 8.22177 6.66663 8.0001V3.83344H8.33329V7.6551L10.5891 9.91094L9.41079 11.0893ZM7.5 0.5C3.365 0.5 0 3.865 0 8C0 12.135 3.365 15.5 7.5 15.5C11.635 15.5 15 12.135 15 8C15 3.865 11.635 0.5 7.5 0.5Z"
        fill="currentColor"
      />
    </Svg>
  );
};
