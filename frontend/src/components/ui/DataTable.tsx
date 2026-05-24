type DataTableProps<T> = {
  columns: { key: keyof T; label: string }[];
  rows: T[];
};

export function DataTable<T extends Record<string, string | number>>({
  columns,
  rows,
}: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-100">
          <tr>
            {columns.map((column) => (
              <th
                key={String(column.key)}
                className="px-4 py-3 text-left font-semibold text-slate-700"
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index} className="border-t border-slate-200">
              {columns.map((column) => (
                <td key={String(column.key)} className="px-4 py-3 text-slate-600">
                  {String(row[column.key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
