export interface ReprintRecord {
  requested_date: string | null;
  order_number: string | null;
  product_type: string | null;
  sub_type: string | null;
  facility: string | null;
  reprint_reason: string | null;
  shipping_country: string | null;
  shipping_service: string | null;
  monumber: string | null;
  conumber: string | null;
  order_value: number | null;
}

export function exportToCSV(records: ReprintRecord[], filename: string = 'reprints.csv') {
  if (records.length === 0) {
    alert('No records to export');
    return;
  }

  // Define CSV headers
  const headers = [
    'Requested Date',
    'Order Number',
    'Product Type',
    'Sub Type',
    'Facility',
    'Reprint Reason',
    'Shipping Country',
    'Shipping Service',
    'MONumber',
    'CONumber',
    'Order Value',
  ];

  // Convert records to CSV rows
  const csvRows = [
    headers.join(','),
    ...records.map((record) => {
      return [
        record.requested_date || '',
        record.order_number || '',
        record.product_type || '',
        record.sub_type || '',
        record.facility || '',
        record.reprint_reason || '',
        record.shipping_country || '',
        record.shipping_service || '',
        record.monumber || '',
        record.conumber || '',
        record.order_value?.toString() || '',
      ]
        .map((field) => {
          // Escape commas and quotes in fields
          const stringField = String(field);
          if (stringField.includes(',') || stringField.includes('"') || stringField.includes('\n')) {
            return `"${stringField.replace(/"/g, '""')}"`;
          }
          return stringField;
        })
        .join(',');
    }),
  ];

  // Create CSV content
  const csvContent = csvRows.join('\n');

  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

