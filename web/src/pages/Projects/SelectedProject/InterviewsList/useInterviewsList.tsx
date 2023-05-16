import { useEffect, useState } from "react";
import { baseApiUrl, interviewEndPoints } from "../../../../api/apiEndpoints";

interface rowProps {
  [key: string]: string | number;
}

const columns = [
  {
    headerName: "Title",
    field: "title",
  },
  {
    headerName: "Date",
    field: "date",
  },
  {
    headerName: "Length",
    field: "length",
  },
];
export default function useInterviewsList() {
  const [rows, setRows] = useState<rowProps[]>([]);

  async function getInterviewsList() {
    const res = await fetch(baseApiUrl + interviewEndPoints.interviewList, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
    });

    const data = await res.json();
    const rows = data.map((row: rowProps, index: number) => {
      return {
        id: row["id"],
        title: row["title"],
        date: `Feb ${index + 1}`,
        length: `${index + 1 * 10 + 1} mins`,
      };
    });
    setRows(rows);
  }

  useEffect(() => {
    getInterviewsList();
  }, []);

  return {
    rows,
    columns,
  };
}
