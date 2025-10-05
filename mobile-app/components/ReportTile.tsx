import { ReactNode } from "react";
import { Pressable, Text, View } from "react-native";

interface ReportTileProps {
  title: string;
  icon: ReactNode;
  onPress: () => void;
}

export const ReportTile = ({ icon, title, onPress }: ReportTileProps) => {
  return (
    <Pressable
      onPress={onPress}
      className="flex h-[166px] w-[48%] flex-col items-center justify-center gap-[12px] rounded-md bg-white"
    >
      <View
        className={`flex aspect-square w-[100px] items-center justify-center  rounded-full border-[5px] border-solid border-[#fafbfd] bg-[#f1f3f8]`}
      >
        {icon}
      </View>
      <Text className="text-center text-[16px] font-bold">{title}</Text>
    </Pressable>
  );
};
