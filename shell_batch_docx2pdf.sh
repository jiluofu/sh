for file in "$@"
do
    # 只处理 docx
    case "$file" in
        *.docx|*.DOCX)
            ;;
        *)
            continue
            ;;
    esac

    # 跳过 Word 临时文件
    filename=$(basename "$file")
    [[ "$filename" == '~$'* ]] && continue

    pdf="${file%.*}.pdf"

    echo "转换：$file"
    echo "输出：$pdf"

    osascript - "$file" "$pdf" <<'APPLESCRIPT'
on run argv

    set inputPath to item 1 of argv
    set outputPath to item 2 of argv

    set inputFile to POSIX file inputPath
    set outputFile to POSIX file outputPath
    set outputHFS to outputFile as text

    tell application "Microsoft Word"

        activate

        open inputFile

        delay 1

        set theDoc to active document

        save as theDoc file name outputHFS file format format PDF

        close theDoc saving no

    end tell

end run
APPLESCRIPT

done