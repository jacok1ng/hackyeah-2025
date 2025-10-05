import { BackArrowIcon, NotificationsSettingsIcon } from "@/assets/icons";
import { ScrollView, Text, View, Switch, Pressable } from "react-native";
import { useState } from "react";

export default function NotificationSettings() {
  const [pushNotifications, setPushNotifications] = useState(true);
  const [journeyNotifications, setJourneyNotifications] = useState(true);
  const [delayNotifications, setDelayNotifications] = useState(true);
  const [emergencyNotifications, setEmergencyNotifications] = useState(true);
  const [promotionalNotifications, setPromotionalNotifications] =
    useState(false);

  return (
    <ScrollView
      contentContainerStyle={{
        paddingInline: 16,
        paddingBlock: 32,
      }}
    >
      <View className="flex flex-col gap-6">
        {/* Sekcja podstawowych powiadomień */}
        <View className="flex flex-row justify-center">
          <View className="flex aspect-square w-[50px] items-center justify-center rounded-full bg-white">
            <NotificationsSettingsIcon />
          </View>
        </View>
        <Text className=" text-center text-[20px] font-semibold">
          Ustawienia powiadomień
        </Text>
        <Text className=" text-center">
          Wybierz, które powiadomienia chcesz otrzymywać i gdzie
        </Text>
        <View className="rounded-lg bg-white p-4">
          <Text className="mb-4 text-lg font-semibold text-gray-800">
            Podstawowe powiadomienia
          </Text>

          <View className="flex flex-row items-center justify-between py-3">
            <View>
              <Text className="text-base font-medium">Powiadomienia push</Text>
              <Text className="text-sm text-gray-600">
                Otrzymuj wszystkie powiadomienia
              </Text>
            </View>
            <Switch
              value={pushNotifications}
              onValueChange={setPushNotifications}
              trackColor={{ false: "#E1E2E6", true: "#4A63AA" }}
              thumbColor={pushNotifications ? "#ffffff" : "#B6BFD6"}
            />
          </View>

          <View className="flex flex-row items-center justify-between py-3">
            <View>
              <Text className="text-base font-medium">
                Powiadomienia o podróżach
              </Text>
              <Text className="text-sm text-gray-600">
                Informacje o rozpoczęciu i zakończeniu podróży
              </Text>
            </View>
            <Switch
              value={journeyNotifications}
              onValueChange={setJourneyNotifications}
              trackColor={{ false: "#E1E2E6", true: "#4A63AA" }}
              thumbColor={journeyNotifications ? "#ffffff" : "#B6BFD6"}
            />
          </View>
        </View>

        {/* Sekcja powiadomień o zakłóceniach */}
        <View className="rounded-lg bg-white p-4">
          <Text className="mb-4 text-lg font-semibold text-gray-800">
            Powiadomienia o zakłóceniach
          </Text>

          <View className="flex flex-row items-center justify-between py-3">
            <View>
              <Text className="text-base font-medium">Opóźnienia i zmiany</Text>
              <Text className="text-sm text-gray-600">
                Informacje o opóźnieniach i zmianach tras
              </Text>
            </View>
            <Switch
              value={delayNotifications}
              onValueChange={setDelayNotifications}
              trackColor={{ false: "#E1E2E6", true: "#4A63AA" }}
              thumbColor={delayNotifications ? "#ffffff" : "#B6BFD6"}
            />
          </View>

          <View className="flex flex-row items-center justify-between py-3">
            <View>
              <Text className="text-base font-medium">
                Powiadomienia awaryjne
              </Text>
              <Text className="text-sm text-gray-600">
                Ważne informacje o zakłóceniach
              </Text>
            </View>
            <Switch
              value={emergencyNotifications}
              onValueChange={setEmergencyNotifications}
              trackColor={{ false: "#E1E2E6", true: "#4A63AA" }}
              thumbColor={emergencyNotifications ? "#ffffff" : "#B6BFD6"}
            />
          </View>
        </View>

        {/* Sekcja powiadomień promocyjnych */}
        <View className="rounded-lg bg-white p-4">
          <Text className="mb-4 text-lg font-semibold text-gray-800">
            Powiadomienia promocyjne
          </Text>

          <View className="flex flex-row items-center justify-between py-3">
            <View>
              <Text className="text-base font-medium">Oferty i promocje</Text>
              <Text className="text-sm text-gray-600">
                Informacje o zniżkach i promocjach
              </Text>
            </View>
            <Switch
              value={promotionalNotifications}
              onValueChange={setPromotionalNotifications}
              trackColor={{ false: "#E1E2E6", true: "#4A63AA" }}
              thumbColor={promotionalNotifications ? "#ffffff" : "#B6BFD6"}
            />
          </View>
        </View>

        {/* Sekcja godzin powiadomień */}
        <View className="rounded-lg bg-white p-4">
          <Text className="mb-4 text-lg font-semibold text-gray-800">
            Godziny powiadomień
          </Text>

          <Pressable className="py-3">
            <View className="flex flex-row items-center justify-between">
              <View>
                <Text className="text-base font-medium">Cisza nocna</Text>
                <Text className="text-sm text-gray-600">22:00 - 07:00</Text>
              </View>
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#FBC535"
              />
            </View>
          </Pressable>

          <Pressable className="py-3">
            <View className="flex flex-row items-center justify-between">
              <Text className="text-base font-medium">Dostosuj godziny</Text>
              <BackArrowIcon
                style={{ transform: [{ rotate: "180deg" }] }}
                color="#FBC535"
              />
            </View>
          </Pressable>
        </View>
      </View>
    </ScrollView>
  );
}
