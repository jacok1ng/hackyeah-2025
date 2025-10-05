import { ReportType } from "@/types/report";

export const getReportTypeColor = (reportType: ReportType) => {
  switch (reportType) {
    case "animal":
      return { main: "#30c3e5", light: "#d8f5fc" };
    case "crowded-passage":
      return { main: "#e0c815", light: "#faf5d1" };
    case "medical-help":
      return { main: "#a264c9", light: "#f3e5fd" };
    case "traffic-jam":
      return { main: "#e99b27", light: "#ffe8c4" };
    case "accident":
      return { main: "#E94A65", light: "#ffced6" };
    case "dirty-vehicle":
      return { main: "#c49b58", light: "#f2ece3" };
    default:
      return { main: "#000000", light: "#000000" }; // Default color if reportType is not recognized
  }
};
