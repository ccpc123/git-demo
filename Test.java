import java.io.IOException;

class Test{
    public static void main(String[] args) throws IOException {
        String exe = "python";
        String command = "./wallpaper.py";
        
        Process process = Runtime.getRuntime().exec("python wallpaper.py");
        process.destroy();
        

    }
}