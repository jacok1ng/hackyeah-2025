import { BackArrowIcon, FireIcon, RankIcon } from "@/assets/icons";
import { ScrollView, Text, View } from "react-native";

export default function Tab() {
  return (
    <ScrollView
      contentContainerStyle={{
        paddingInline: 16,
        paddingBlock: 32,
      }}
    >
      <View className="flex flex-col items-center">
        {/* <View className="self-start rounded-full bg-[#fdfdfd] p-[15px]"> */}
        {/* <View className="self-start rounded-full bg-white p-[10px]"> */}
        <View className="flex aspect-square w-[120px] items-center justify-center rounded-full border-[3px] border-solid border-[#b0c6f9] bg-[#ebeef7]">
          <RankIcon color="#4A63AA" width={100} height={80} />
          {/* </View> */}
          {/* </View> */}
        </View>
        <Text className="mt-[32px] text-center text-[22px] font-semibold">
          Jan Kowalski
        </Text>
        <View className="mt-[18px] flex flex-row items-center justify-center gap-[8px]">
          <Text>Twoja ranga:</Text>
          <View className="flex flex-row gap-[8px] rounded-[32px] bg-[#3C4F86] px-[16px] py-[6px]">
            <RankIcon width={12} height={17} color="white" />
            <Text className="font-medium text-white">Konduktor</Text>
          </View>
        </View>

        <View className="mt-[32px] flex flex-row items-center justify-center gap-[8px]">
          <Text className="">Twój streak:</Text>
          <View className="flex flex-row gap-[8px] rounded-[32px] bg-[#ECBA9B] px-[16px] py-[6px]">
            <FireIcon width={14} height={20} color="#C65814" />
            <Text className=" font-medium text-black">3 dni z rzędu</Text>
          </View>
        </View>

        <View className="mt-[14px] flex flex-row gap-[8px]">
          <View className="flex aspect-square w-[38px] items-center justify-center rounded-full bg-[#ECBA9B]">
            <FireIcon width={14} height={20} color="#C65814" />
          </View>
          <View className="flex aspect-square w-[38px] items-center justify-center rounded-full bg-[#ECBA9B]">
            <FireIcon width={14} height={20} color="#C65814" />
          </View>
          <View className="flex aspect-square w-[38px] items-center justify-center rounded-full bg-[#ECBA9B]">
            <FireIcon width={14} height={20} color="#C65814" />
          </View>
          <View className="flex aspect-square w-[38px] items-center justify-center rounded-full bg-[#E1E2E6]">
            <FireIcon width={14} height={20} color="#B6BFD6" />
          </View>
          <View className="flex aspect-square w-[38px] items-center justify-center rounded-full bg-[#E1E2E6]">
            <FireIcon width={14} height={20} color="#B6BFD6" />
          </View>
          <View className="flex aspect-square w-[38px] items-center justify-center rounded-full bg-[#E1E2E6]">
            <FireIcon width={14} height={20} color="#B6BFD6" />
          </View>
          <View className="flex aspect-square w-[38px] items-center justify-center rounded-full bg-[#E1E2E6]">
            <FireIcon width={14} height={20} color="#B6BFD6" />
          </View>
        </View>

        <Text className="mt-[8px]">
          Jeszcze <Text className="font-bold">4</Text> dni, aby odblokować
          nagrodę!
        </Text>

        <View className="mt-[32px] flex gap-[14px] rounded-md">
          <View className="w-full flex-row justify-between bg-white px-[18px] py-[14px]">
            <View>
              <Text className="text-[14px] font-semibold">Ustawienia</Text>
            </View>
            <BackArrowIcon
              style={{ transform: [{ rotate: "180deg" }] }}
              color="#FBC535"
            />
          </View>

          <View className="w-full flex-row justify-between bg-white px-[18px] py-[14px]">
            <View>
              <Text className="text-[14px] font-semibold">Płatności</Text>
            </View>
            <BackArrowIcon
              style={{ transform: [{ rotate: "180deg" }] }}
              color="#FBC535"
            />
          </View>

          <View className="w-full flex-row justify-between bg-white px-[18px] py-[14px]">
            <View>
              <Text className="text-[14px] font-semibold">Moje potrzeby</Text>
            </View>
            <BackArrowIcon
              style={{ transform: [{ rotate: "180deg" }] }}
              color="#FBC535"
            />
          </View>

          <View className="w-full flex-row justify-between bg-white px-[18px] py-[14px]">
            <View>
              <Text className="text-[14px] font-semibold">Ranga i odznaki</Text>
            </View>
            <BackArrowIcon
              style={{ transform: [{ rotate: "180deg" }] }}
              color="#FBC535"
            />
          </View>

          <View className="w-full flex-row justify-between bg-white px-[18px] py-[14px]">
            <View>
              <Text className="text-[14px] font-semibold">O aplikacji</Text>
            </View>
            <BackArrowIcon
              style={{ transform: [{ rotate: "180deg" }] }}
              color="#FBC535"
            />
          </View>
        </View>
      </View>
    </ScrollView>
  );
}
