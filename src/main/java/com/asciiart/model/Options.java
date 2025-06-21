package com.asciiart.model;

import picocli.CommandLine;
import picocli.CommandLine.Option;

@CommandLine.Command(name = "AsciiArtGenerator", mixinStandardHelpOptions = true)
public class Options {
    @Option(names = {"-i", "--input"}, description = "输入图片路径", required = true)
    private String inputPath;

    @Option(names = {"-o", "--output"}, description = "输出图片路径", defaultValue = "output.jpg")
    private String outputPath;

    @Option(names = {"-l", "--language"}, description = "字符集语言 (english/chinese/custom)", defaultValue = "chinese")
    private String language;

    @Option(names = "--custom_text", description = "自定义文本 (当language=custom时使用)")
    private String customText;

    @Option(names = "--color", description = "启用彩色输出")
    private boolean color;

    @Option(names = "--portrait", description = "竖屏模式优化")
    private boolean portrait;

    @Option(names = "--columns", description = "字符列数", defaultValue = "100")
    private int numColumns;

    public String getInputPath() { return inputPath; }
    public String getOutputPath() { return outputPath; }
    public String getLanguage() { return language; }
    public String getCustomText() { return customText; }
    public boolean isColor() { return color; }
    public boolean isPortrait() { return portrait; }
    public int getNumColumns() { return numColumns; }
}
