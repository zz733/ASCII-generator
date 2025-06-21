package com.asciiart;

import com.asciiart.model.Options;
import com.asciiart.util.ImageUtils;
import com.asciiart.util.TextRenderer;
import org.bytedeco.opencv.opencv_core.Mat;

import javax.imageio.ImageIO;
import java.io.File;

public class AsciiArtGenerator implements Runnable {
    private final Options options;

    public AsciiArtGenerator(Options options) {
        this.options = options;
    }

    @Override
    public void run() {
        try {
            Mat image = ImageUtils.loadImage(options.getInputPath(), options.isColor());
            if (options.isPortrait()) {
                ImageUtils.rotateIfNeeded(image, true);
            }
            TextRenderer renderer = new TextRenderer(
                options.isColor(),
                options.getLanguage(),
                options.getCustomText()
            );
            var result = renderer.render(image, options.getNumColumns());
            String outputPath = options.getOutputPath();
            String format = outputPath.substring(outputPath.lastIndexOf('.') + 1);
            File outputFile = new File(outputPath);
            ImageIO.write(result, format, outputFile);
            System.out.println("处理完成！输出文件: " + outputFile.getAbsolutePath());
        } catch (Exception e) {
            System.err.println("生成ASCII艺术时出错: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        Options options = new Options();
        try {
            new picocli.CommandLine(options).parseArgs(args);
            if (args.length == 0 || new picocli.CommandLine(options).isUsageHelpRequested()) {
                new picocli.CommandLine(options).usage(System.out);
                return;
            }
            new AsciiArtGenerator(options).run();
        } catch (Exception e) {
            System.err.println("参数错误: " + e.getMessage());
            new picocli.CommandLine(options).usage(System.err);
            System.exit(1);
        }
    }
}
