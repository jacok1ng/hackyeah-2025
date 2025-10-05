import { StarIcon } from "@/assets/icons";
import { ReportType } from "@/types/report";
import React from "react";
import {
  Modal,
  View,
  Text,
  TouchableWithoutFeedback,
  Pressable,
} from "react-native";
import { ReportIcon } from "./ReportIcon";
import { getReportTypeColor } from "@/helpers";
import { useRouter } from "expo-router";

type Props = {
  onClose?: () => void;
  reportType: ReportType | null;
  visible: boolean;
};

export const ReportConfirmationModal: React.FC<Props> = ({
  visible,
  onClose,
  reportType,
}) => {
  const router = useRouter();
  if (reportType === null) return null;
  const { light, main } = getReportTypeColor(reportType);

  return (
    <Modal
      visible={!!visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <TouchableWithoutFeedback onPress={onClose}>
        <View className="flex-1 items-center justify-center bg-black/50">
          <TouchableWithoutFeedback>
            <View className="flex w-[90%] items-center rounded-md bg-white p-[18px] shadow-sm">
              <Text className="text-center text-[24px] font-bold">Gotowe!</Text>
              <Text className="mt-[8px] text-center text-[14px] text-[#595959]">
                Twoje zgłoszenie zostało wysłane. Dzięki, że pomagasz innym
                podróżnym!
              </Text>
              <View
                className={`my-[40px] flex aspect-square w-[50%] items-center justify-center  rounded-full`}
                style={{
                  backgroundColor: main,
                  borderWidth: 13,
                  borderColor: light, // 35% opacity of the bg color
                }}
              >
                <ReportIcon
                  reportType={reportType}
                  color="#1E1E1E"
                  width={80}
                  height={80}
                />
              </View>
              <View className="flex w-full flex-row items-center justify-between">
                <Text className="text-[16px] font-semibold">Zyskujesz</Text>
                <View className="flex flex-row items-center gap-[8px] rounded-sm bg-[#F1F3F8] px-[12px] py-[10px]">
                  <Text className="text-[14px] font-bold">+ 5 punktów</Text>
                  <StarIcon width="16" color="#4A63AA" />
                </View>
              </View>

              <Pressable
                onPress={() => {
                  onClose?.();
                  router.navigate("/(tabs)");
                }}
                className="mt-[22px] flex h-[50px] w-full items-center justify-center rounded-md bg-[#FBC535]"
              >
                <Text className="text-[16px] font-bold text-white">
                  Zamknij
                </Text>
              </Pressable>
            </View>
          </TouchableWithoutFeedback>
        </View>
      </TouchableWithoutFeedback>
    </Modal>
  );
};
