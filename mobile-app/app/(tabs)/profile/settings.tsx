import { BackArrowIcon, SettingsIcon } from "@/assets/icons";
import { ScrollView, Text, View, Pressable } from "react-native";
import { Link } from "expo-router";

export default function Settings() {
  return (
    <ScrollView
      contentContainerStyle={{
        paddingInline: 16,
        paddingBlock: 32,
      }}
    >
      <View className="flex flex-col items-center">
        <View className="flex aspect-square w-[50px] items-center justify-center rounded-full bg-white">
          <SettingsIcon />
        </View>
        <Text className="mt-[16px] text-[20px] font-semibold">Ustawienia</Text>
        <Text className="mt-[5px]">Dostosuj ustawienia</Text>
        <View className="mt-[32px] flex w-full gap-[14px] rounded-md">
          <Pressable
            className="w-full flex-row justify-between bg-white px-[18px] py-[14px]"
            onPress={() => {
              /* TODO: Navigate to personal data */
            }}
          >
            <View>
              <Text className="text-[14px] font-semibold">Moje Dane</Text>
            </View>
            <BackArrowIcon
              style={{ transform: [{ rotate: "180deg" }] }}
              color="#FBC535"
            />
          </Pressable>

          <Link href="/(tabs)/profile/notifications" asChild>
            <Pressable className="w-full flex-row justify-between bg-white px-[18px] py-[14px]">
              <View>
                <Text className="text-[14px] font-semibold">
                  Ustawienia powiadomień
                </Text>
              </View>
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#FBC535"
              />
            </Pressable>
          </Link>

          <Pressable
            className="w-full flex-row justify-between bg-white px-[18px] py-[14px]"
            onPress={() => {
              /* TODO: Navigate to personal data */
            }}
          >
            <View>
              <Text className="text-[14px] font-semibold">
                Preferowany widok aplikacji
              </Text>
            </View>
            <BackArrowIcon
              style={{ transform: [{ rotate: "180deg" }] }}
              color="#FBC535"
            />
          </Pressable>

          <Pressable
            className="w-full flex-row justify-between bg-white px-[18px] py-[14px]"
            onPress={() => {
              /* TODO: Navigate to personal data */
            }}
          >
            <View>
              <Text className="text-[14px] font-semibold">Zmień hasło</Text>
            </View>
            <BackArrowIcon
              style={{ transform: [{ rotate: "180deg" }] }}
              color="#FBC535"
            />
          </Pressable>
        </View>
      </View>
    </ScrollView>
  );
}
