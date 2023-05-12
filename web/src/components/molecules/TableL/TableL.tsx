import { styled } from "@mui/material/styles";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import theme from "../../../theme/theme";
import { edit_pencil__icon } from "../../../assets/icons/svg";
import { useState } from "react";

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
  onEditClick?: (row: rowType) => void;
}

export default function TableL(props: TableLProps) {
  const { columns, rows, onCellClick, onEditClick } = props;
  const [showEditIndex, setShowEditIndex] = useState(-1);
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
          {rows.map((row, rowIndex) => (
            <StyledTableRow
              key={row.name}
              sx={{
                "&:last-child td, &:last-child th": { border: 0 },
                "&:hover": {
                  cursor: "pointer",
                  backgroundColor: theme.palette.grey[100],
                },
              }}
              onClick={() => onCellClick && onCellClick(row)}
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
                  {...(index === 0 && {
                    onMouseEnter: () => setShowEditIndex(rowIndex),
                    onMouseLeave: () => setShowEditIndex(-1),
                  })}
                >
                  {row[column.field]}
                  {onEditClick && showEditIndex === rowIndex && index === 0 && (
                    <img
                      src={edit_pencil__icon}
                      onClick={(e) => {
                        e.stopPropagation();
                        onEditClick(row);
                      }}
                      alt="edit"
                      style={{
                        cursor: "pointer",
                        display: "inline",
                        marginLeft: "5px",
                      }}
                    />
                  )}
                </StyledTableCell>
              ))}
            </StyledTableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
