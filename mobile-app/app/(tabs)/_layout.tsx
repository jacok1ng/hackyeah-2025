import {
  AvatarIcon,
  HearthIcon,
  HomeIcon,
  StatusIcon,
  TicketIcon,
} from "@/assets/icons";
import Header from "@/components/Header";
import { Tabs } from "expo-router";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#FBC535",
        tabBarInactiveTintColor: "#4A63AA",
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          tabBarLabel: "Start",
          header: () => <Header title="Zmiana połączenia" />,
          tabBarIcon: ({ color }) => <HomeIcon color={color} />,
        }}
      />
      <Tabs.Screen
        name="favorites"
        options={{
          tabBarLabel: "Ulubione",
          header: () => <Header title="Ulubione" />,
          tabBarIcon: ({ color }) => <HearthIcon color={color} />,
        }}
      />
      <Tabs.Screen
        name="tickets"
        options={{
          tabBarLabel: "Bilety",
          header: () => <Header title="Bilety" />,
          tabBarIcon: ({ color }) => <TicketIcon color={color} />,
        }}
      />
      <Tabs.Screen
        name="status"
        options={{
          header: () => <Header title="Status" />,
          tabBarLabel: "Status",
          tabBarIcon: ({ color }) => <StatusIcon color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          header: () => <Header title="Mój Profil" />,
          tabBarLabel: "Profil",
          tabBarIcon: ({ color }) => <AvatarIcon color={color} />,
        }}
      />
    </Tabs>
  );
}
