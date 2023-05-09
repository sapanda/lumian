import { styled } from "@mui/material/styles";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import theme from "../../../theme/theme";

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
interface rowType {
  [key: string]: string | number;
}
interface TableLProps {
  columns: {
    headerName: string;
    field: string;
  }[];
  rows: {
    [key: string]: string | number;
  }[];

  onCellClick?: (row: rowType) => void;
}

export default function TableL(props: TableLProps) {
  const { columns, rows, onCellClick } = props;

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
              sx={{
                "&:last-child td, &:last-child th": { border: 0 },
              }}
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
                  sx={{
                    ...(index === 0 && {
                      "&:hover": {
                        cursor: "pointer",
                        color: theme.palette.primary.main,
                      },
                    }),
                  }}
                  {...(index === 0 && {
                    onClick: () => {
                      onCellClick && row && onCellClick(row);
                    },
                  })}
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
