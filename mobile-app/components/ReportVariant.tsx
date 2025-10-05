import { Text, View } from "react-native";
import { ReportTile } from "./ReportTile";
import {
  AnimalIcon,
  GroupIcon,
  HealthIcon,
  ObstacleIcon,
  RoadIcon,
  SprayIcon,
} from "@/assets/icons";
import { Dispatch, SetStateAction } from "react";
import { ReportType } from "@/types/report";

interface ReportVariantProps {
  setReportType: Dispatch<SetStateAction<ReportType | null>>;
}

export const ReportVariant = ({ setReportType }: ReportVariantProps) => {
  return (
    <>
      <View className="mb-[32px] flex flex-col ">
        <Text className="text-center text-[22px] font-bold">Co się stało?</Text>
        <Text className="text-center text-[16px]">
          Wybierz rodzaj zdarzenia
        </Text>
      </View>
      <View className="flex-row flex-wrap gap-[14px]">
        <ReportTile
          title="Wypadek"
          icon={<RoadIcon color="#E94A65" />}
          onPress={() => setReportType("accident")}
        />

        <ReportTile
          title="Utrudnienie/Korek"
          onPress={() => setReportType("traffic-jam")}
          icon={<ObstacleIcon color="#e99b27" />}
        />

        <ReportTile
          title="Zwierzę"
          icon={<AnimalIcon color="#30c3e5" />}
          onPress={() => setReportType("animal")}
        />

        <ReportTile
          title="Przepełniony przejazd"
          icon={<GroupIcon color="#e0c815" />}
          onPress={() => setReportType("crowded-passage")}
        />
        <ReportTile
          title="Brudny pojazd"
          icon={<SprayIcon color="#c49b58" />}
          onPress={() => setReportType("dirty-vehicle")}
        />

        <ReportTile
          title="Pomoc medyczna"
          icon={<HealthIcon color="#a264c9" />}
          onPress={() => setReportType("medical-help")}
        />
      </View>
    </>
  );
};
