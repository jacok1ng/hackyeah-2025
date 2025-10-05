import {
  AnimalIcon,
  GroupIcon,
  HealthIcon,
  ObstacleIcon,
  RoadIcon,
  SprayIcon,
} from "@/assets/icons";
import { ReportType } from "@/types/report";

interface ReportIconProps {
  reportType: ReportType;
  width?: number;
  height?: number;
  color?: string;
}

export const ReportIcon = ({
  reportType,
  width = 26,
  height,
  color,
}: ReportIconProps) => {
  switch (reportType) {
    case "animal":
      return (
        <AnimalIcon width={width} height={height} color={color || "#30c3e5"} />
      );
    case "crowded-passage":
      return (
        <GroupIcon width={width} height={height} color={color || "#e0c815"} />
      );
    case "medical-help":
      return (
        <HealthIcon width={width} height={height} color={color || "#a264c9"} />
      );
    case "traffic-jam":
      return (
        <ObstacleIcon
          width={width}
          height={height}
          color={color || "#e99b27"}
        />
      );
    case "accident":
      return (
        <RoadIcon width={width} height={height} color={color || "#E94A65"} />
      );
    case "dirty-vehicle":
      return (
        <SprayIcon width={width} height={height} color={color || "#c49b58"} />
      );
    default:
      return null;
  }
};
