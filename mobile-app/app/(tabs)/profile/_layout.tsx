import { Stack } from "expo-router";
import Header from "@/components/Header";

export default function ProfileLayout() {
  return (
    <Stack>
      <Stack.Screen
        name="index"
        options={{
          header: () => <Header title="Mój Profil" />,
        }}
      />
      <Stack.Screen
        name="settings"
        options={{
          header: () => <Header title="Ustawienia" />,
        }}
      />
      <Stack.Screen
        name="notifications"
        options={{
          header: () => <Header title="Powiadomienia" />,
        }}
      />
    </Stack>
  );
}
