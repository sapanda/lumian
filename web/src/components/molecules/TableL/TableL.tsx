import { styled } from "@mui/material/styles";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  [`&.${tableCellClasses.head}`]: {
    fontSize: "14px",
    fontWeight: "bold",
    color: theme.palette.common.black,
  },
  [`&.${tableCellClasses.body}`]: {
    fontSize: "12px",
    fontWeight: 400,
  },
}));

const StyledTableRow = styled(TableRow)(() => ({
  border: 0,
  "& > th, & > td": {
    border: 0,
  },
}));

interface TableLProps {
  columns: {
    headerName: string;
    field: string;
  }[];
  rows: {
    [key: string]: string | number;
  }[];
}

export default function TableL(props: TableLProps) {
  const { columns, rows } = props;
  return (
    <TableContainer>
      <Table sx={{ minWidth: 700 }} aria-label="customized table">
        <TableHead>
          <TableRow>
            {columns.map((column, index) => (
              <StyledTableCell
                align={
                  index === 0
                    ? "left"
                    : index === columns.length - 1
                    ? "right"
                    : "center"
                }
              >
                {column.headerName}
              </StyledTableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <StyledTableRow
              key={row.name}
              sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
            >
              {columns.map((column, index) => (
                <StyledTableCell
                  align={
                    index === 0
                      ? "left"
                      : index === columns.length - 1
                      ? "right"
                      : "center"
                  }
                >
                  {row[column.field]}
                </StyledTableCell>
              ))}
            </StyledTableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
