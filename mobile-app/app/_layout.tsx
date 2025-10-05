import { Stack, useRouter } from "expo-router";
import "../global.css";
import { Pressable, StatusBar } from "react-native";
import { BackArrowIcon, BellIcon } from "@/assets/icons";
import Header from "@/components/Header";

export default function RootLayout() {
  const router = useRouter();
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen
        name="report"
        options={{
          title: "Zgłoś zdarzenie",
          // headerLeft: () => (
          //   <Pressable onPress={() => router.back()}>
          //     <BackArrowIcon />
          //   </Pressable>
          // ),
          // headerRight: () => <BellIcon />,
          header: () => <Header title="Zgłoś zdarzenie" />,
        }}
      />
      <StatusBar />
    </Stack>
  );
}
