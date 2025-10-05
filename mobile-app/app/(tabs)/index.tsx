import {
  BackArrowIcon,
  BusIcon,
  ClockIcon,
  DislikeIcon,
  ExclamationMarkIcon,
  LikeIcon,
  MapMarkerIcon,
  Ped12Icon,
  Ped3Icon,
  StarIcon,
  TrainIcon,
  ZoomIcon,
} from "@/assets/icons";
import { ScrollView, Text, View } from "react-native";

export default function Tab() {
  return (
    <View className="flex-1">
      <View className="flex">
        <View className="bg-[#3C4F86] p-[18px]">
          <View className="flex flex-row items-center justify-between rounded-md border-[1px] border-solid border-[#657DC0] bg-[#52659C] px-[12px] py-[18px]">
            <View className="flex">
              <Text className="text-[12px] text-[#a8b2cd]">Początek</Text>
              <Text className="text-[16px] text-white">Rondo Mogilskie</Text>
            </View>
            <MapMarkerIcon color="#FBC535" />
          </View>

          <View className="mt-[12px] flex flex-row items-center justify-between rounded-md border-[1px] border-solid border-[#657DC0] bg-[#52659C] px-[12px] py-[18px]">
            <View className="flex">
              <Text className="text-[12px] text-[#a8b2cd]">Koniec</Text>
              <Text className="text-[16px] text-white">Expo Kraków</Text>
            </View>
            <StarIcon color="#FBC535" />
          </View>

          <Text className="mt-[18px] text-[16px] text-white">
            Dzisiaj, 17:42
          </Text>
        </View>
      </View>
      <ScrollView
        className="px-[16px] py-[32px]"
        contentContainerStyle={{ paddingBottom: 32 }}
      >
        <Text className="text-center text-[22px] font-bold">
          Twoje alternatywy
        </Text>
        <Text className="mb-[32px] mt-[5px] text-center text-[14px]">
          Wybierz jedną z proponowanych tras
        </Text>
        <View className="flex gap-[14px]">
          <View className="flex gap-[14px] rounded-md bg-white p-[18px]">
            <View className="flex flex-row justify-between">
              <Text className="text-[16px] font-bold">17:57 - 18:44</Text>
              <View className="flex flex-row items-center">
                <ClockIcon color="#92A3D2" />
                <Text className="ml-[6px] text-[16px] font-semibold">
                  47 min
                </Text>
              </View>
            </View>
            <View className="flex flex-row items-center gap-[8px]">
              <Ped3Icon color="#3C4F86" />
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#3C4F86] p-[8px]">
                <TrainIcon color="white" />
                <Text className="text-[12px] text-white">IC 3802</Text>
              </View>
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <Ped12Icon color="#3C4F86" />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#8E6BED] p-[8px]">
                <BusIcon color="white" />
                <ZoomIcon color="white" />
              </View>
            </View>
            <View className="rounded-xs flex flex-row self-start bg-[#D1F0E3] p-[8px]">
              <LikeIcon color="#0CB770" />
              <Text className="ml-[4px] text-[12px] font-bold text-[#0CB770]">
                Najszybsza
              </Text>
            </View>
          </View>

          <View className="flex gap-[14px] rounded-md bg-white p-[18px]">
            <View className="flex flex-row justify-between">
              <Text className="text-[16px] font-bold">17:57 - 18:44</Text>
              <View className="flex flex-row items-center">
                <ClockIcon color="#92A3D2" />
                <Text className="ml-[6px] text-[16px] font-semibold">
                  47 min
                </Text>
              </View>
            </View>
            <View className="flex flex-row items-center gap-[8px]">
              <Ped3Icon color="#3C4F86" />
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#3C4F86] p-[8px]">
                <TrainIcon color="white" />
                <Text className="text-[12px] text-white">IC 3802</Text>
              </View>
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <Ped12Icon color="#3C4F86" />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#E8E7E7] p-[8px]">
                <BusIcon color="#595959" />
                <Text className="text-[12px] text-[#595959]">37</Text>
              </View>
            </View>
          </View>

          <View className="flex gap-[14px] rounded-md bg-white p-[18px]">
            <View className="flex flex-row justify-between">
              <Text className="text-[16px] font-bold">17:57 - 18:44</Text>
              <View className="flex flex-row items-center">
                <ClockIcon color="#92A3D2" />
                <Text className="ml-[6px] text-[16px] font-semibold">
                  47 min
                </Text>
              </View>
            </View>
            <View className="flex flex-row items-center gap-[8px]">
              <Ped3Icon color="#3C4F86" />
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#3C4F86] p-[8px]">
                <TrainIcon color="white" />
                <Text className="text-[12px] text-white">IC 3802</Text>
              </View>
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <Ped12Icon color="#3C4F86" />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#E8E7E7] p-[8px]">
                <BusIcon color="#595959" />
                <Text className="text-[12px] text-[#595959]">37</Text>
              </View>
            </View>
          </View>

          <View className="flex gap-[14px] rounded-md bg-white p-[18px]">
            <View className="flex flex-row justify-between">
              <Text className="text-[16px] font-bold">17:57 - 18:44</Text>
              <View className="flex flex-row items-center">
                <ClockIcon color="#92A3D2" />
                <Text className="ml-[6px] text-[16px] font-semibold">
                  47 min
                </Text>
              </View>
            </View>
            <View className="flex flex-row items-center gap-[8px]">
              <Ped3Icon color="#3C4F86" />
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#3C4F86] p-[8px]">
                <TrainIcon color="white" />
                <Text className="text-[12px] text-white">IC 3802</Text>
              </View>
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <Ped12Icon color="#3C4F86" />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#E8E7E7] p-[8px]">
                <BusIcon color="#595959" />
                <Text className="text-[12px] text-[#595959]">37</Text>
              </View>
            </View>
            <View className="flex flex-row gap-[6px]">
              <View className="rounded-xs flex flex-row self-start bg-[#EDEDED] p-[8px]">
                <DislikeIcon color="#595959" />
                <Text className="ml-[4px] text-[12px] font-bold text-[#595959]">
                  Dłusza
                </Text>
              </View>
              <View className="rounded-xs flex flex-row self-start bg-[#FCE9CF] p-[8px]">
                <ExclamationMarkIcon color="#E59A34" />
                <Text className="ml-[4px] text-[12px] font-bold text-[#E59A34]">
                  +5 min opóźnienia
                </Text>
              </View>
            </View>
          </View>

          <View className="flex gap-[14px] rounded-md bg-white p-[18px]">
            <View className="flex flex-row justify-between">
              <Text className="text-[16px] font-bold">17:57 - 18:44</Text>
              <View className="flex flex-row items-center">
                <ClockIcon color="#92A3D2" />
                <Text className="ml-[6px] text-[16px] font-semibold">
                  47 min
                </Text>
              </View>
            </View>
            <View className="flex flex-row items-center gap-[8px]">
              <Ped3Icon color="#3C4F86" />
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#3C4F86] p-[8px]">
                <TrainIcon color="white" />
                <Text className="text-[12px] text-white">IC 3802</Text>
              </View>
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#AEB4C1"
              />
              <Ped12Icon color="#3C4F86" />
              <View className="flex flex-row items-center gap-[4px] rounded-sm bg-[#E8E7E7] p-[8px]">
                <BusIcon color="#595959" />
                <Text className="text-[12px] text-[#595959]">37</Text>
              </View>
            </View>
            <View className="flex flex-row gap-[6px]">
              <View className="rounded-xs flex flex-row self-start bg-[#EDEDED] p-[8px]">
                <DislikeIcon color="#595959" />
                <Text className="ml-[4px] text-[12px] font-bold text-[#595959]">
                  Dłusza
                </Text>
              </View>
            </View>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}
