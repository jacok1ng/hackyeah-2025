import { ReportConfirmationModal } from "@/components/ReportConfirmationModal";
import { ReportForm } from "@/components/ReportForm";
import { ReportVariant } from "@/components/ReportVariant";
import { ReportType } from "@/types/report";
import { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";

export default function Tab() {
  const [reportType, setReportType] = useState<ReportType | null>(null);
  const [showConfirmationModal, setShowConfirmationModal] = useState(false);

  return (
    <>
      <ReportConfirmationModal
        visible={showConfirmationModal}
        reportType={reportType}
        onClose={() => {
          setShowConfirmationModal(false);
          setReportType(null);
        }}
      />
      <View className="relative flex flex-col">
        <ScrollView
          className=" mb-[32px] px-[16px] pt-[32px]"
          contentContainerStyle={{ paddingBottom: 206 }}
        >
          <View className="mb-[12px] flex flex-1 flex-row items-center justify-center gap-[6px]">
            <View
              className={`h-[8px] w-[31px] rounded-[8px] ${reportType !== null ? "w-[8px] bg-[#D0D0D0]" : "w-[31px] bg-[#FBC535] "}`}
            ></View>
            <View
              className={`h-[8px] w-[31px] rounded-[8px] ${reportType !== null ? "w-[31px] bg-[#FBC535] " : "w-[8px] bg-[#D0D0D0]"}`}
            ></View>
          </View>
          {reportType !== null ? (
            <ReportForm reportType={reportType} />
          ) : (
            <ReportVariant setReportType={setReportType} />
          )}
        </ScrollView>
        {reportType !== null && (
          <View className="absolute bottom-[106px] left-0 h-[106px] w-full bg-white px-[18px]">
            <Pressable
              onPress={() => setShowConfirmationModal(true)}
              className="mb-[32px] mt-[12px] flex h-[50px] items-center justify-center rounded-md bg-[#FBC535]"
            >
              <Text className="text-[16px] font-bold text-white">Zgłoś</Text>
            </Pressable>
          </View>
        )}
      </View>
    </>
  );
}
