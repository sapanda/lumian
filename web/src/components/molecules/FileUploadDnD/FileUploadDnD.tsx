import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface Accept {
  [key: string]: string[];
}
interface FileUploadDnDProps {
  id?: string;
  children: React.ReactNode;
  onUpload: (files: File[]) => void;
  uploaderStyles?: React.CSSProperties;
  extensions?: Accept;
}
export default function FileUploadDnD(props: FileUploadDnDProps) {
  const {
    id = "file-uploader",
    children,
    onUpload,
    uploaderStyles = {},
    extensions,
  } = props;

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Do something with the files
      const uploadedFiles = acceptedFiles;

      onUpload(uploadedFiles);
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: extensions ? extensions : undefined,
  });
  return (
    <div
      {...getRootProps()}
      style={{
        filter: isDragActive ? "brightness(0.8)" : "brightness(1)",
        background: isDragActive ? "#E5E5E5" : "#FFFFFF",
        border: "1px dashed #252525",
        borderRadius: "12px",
        width: "100%",
        ...uploaderStyles,
      }}
    >
      {children}

      <input {...getInputProps()} id={id} />
    </div>
  );
}
