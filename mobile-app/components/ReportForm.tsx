import { Pressable, Text, TextInput, View } from "react-native";
import {
  AnimalIcon,
  BackArrowIcon,
  CameraIcon,
  CheckmarkIcon,
  GroupIcon,
  HealthIcon,
  ObstacleIcon,
  RoadIcon,
  SprayIcon,
} from "@/assets/icons";

import { ReportType } from "@/types/report";
import { useMemo } from "react";

const getReportDetails = (reportType: ReportType) => {
  switch (reportType) {
    case "animal":
      return {
        text: "Zwierzę",
        icon: <AnimalIcon width="26" color="#30c3e5" />,
      };
    case "crowded-passage":
      return {
        text: "Przepełniony pojazd",
        icon: <GroupIcon width="26" color="#e0c815" />,
      };
    case "medical-help":
      return {
        text: "Pomoc medyczna",
        icon: <HealthIcon width="26" color="#a264c9" />,
      };
    case "traffic-jam":
      return {
        text: "Korek",
        icon: <ObstacleIcon width="26" color="#e99b27" />,
      };
    case "accident":
      return { text: "Wypadek", icon: <RoadIcon width="26" color="#E94A65" /> };
    case "dirty-vehicle":
      return {
        text: "Brudny pojazd",
        icon: <SprayIcon width="26" color="#c49b58" />,
      };
    default:
      return null;
  }
};

interface ReportFormProps {
  reportType: ReportType;
}

export const ReportForm = ({ reportType }: ReportFormProps) => {
  const details = useMemo(
    () => getReportDetails(reportType) || { icon: null, text: "" },
    [reportType],
  );

  return (
    <View className="flex flex-col">
      <View className="mb-[32px] flex flex-col ">
        <Text className="text-center text-[22px] font-bold">Podsumowanie</Text>
        <Text className="text-center text-[16px]">
          Pomóż nam lepiej zrozumieć zdarzenie
        </Text>
      </View>
      <View className="flex flex-col gap-[14px]">
        <View className="rounded-md bg-white p-[18px]">
          <View className="flex flex-row justify-between">
            <Text className="text-[16px] font-bold">Zdarzenie</Text>
            <View className="flex flex-row items-center gap-[6px]">
              <BackArrowIcon width="8" />
              <Text className="text-[16px] font-bold text-[#FBC535]">
                Zmień
              </Text>
            </View>
          </View>
          <View className="mt-[12px] flex flex-row items-center justify-between rounded-sm bg-[#F1F3F8] px-[12px] py-[11px]">
            <Text className="text-[14px]">Rodzaj zdarzenia:</Text>
            <View className="flex flex-row items-center gap-[13px]">
              <Text className="font-bold">{details.text}</Text>
              {details.icon}
            </View>
          </View>
        </View>

        <View className="rounded-md bg-white p-[18px]">
          <Text className="text-[16px] font-bold">Lokalizacja GPS</Text>
          <Text className="mt-[4px] text-[12px] text-[#595959]">
            Twoja lokalizacja zostanie użyta do potwierdzenia wiarygodności
          </Text>
          <View className="mt-[12px] flex flex-row items-center justify-between rounded-sm bg-[#F1F3F8] px-[12px] py-[11px]">
            <Text className="text-[14px]">Status:</Text>
            <View className="flex flex-row items-center gap-[13px]">
              <Text className="font-bold">Zgodnie z rozkładem</Text>
              <CheckmarkIcon />
            </View>
          </View>
        </View>

        <View className="rounded-md bg-white p-[18px]">
          <View className="flex flex-row items-center justify-between gap-[6px]">
            <Text className="text-[16px] font-bold">Zrób zdjęcie</Text>
            <Text className=" text-[12px] text-[#595959]">Opcjonalne</Text>
          </View>
          <Text className="mb-[12px] mt-[4px] text-[12px] text-[#595959]">
            Pokaż obiekt/miejsce zdarzenia
          </Text>
          <Pressable className="border-px flex flex-row items-center justify-center gap-[10px] rounded-sm border-[2px] border-solid border-[#FBC535] py-[13px]">
            <CameraIcon />
            <Text className="text-[16px] font-bold">Zrób zdjęcie</Text>
          </Pressable>
        </View>

        <View className="rounded-md bg-white p-[18px]">
          <View className="flex flex-row items-center justify-between gap-[6px]">
            <Text className="text-[16px] font-bold">Dodaj komentarz</Text>
            <Text className=" text-[12px] text-[#595959]">Opcjonalne</Text>
          </View>
          <Text className="mb-[12px] mt-[4px] text-[12px] text-[#595959]">
            Opisz zaistniałą sytuację
          </Text>
          <TextInput className="h-[50px] rounded-md border-[1px]" />
        </View>
      </View>
    </View>
  );
};
