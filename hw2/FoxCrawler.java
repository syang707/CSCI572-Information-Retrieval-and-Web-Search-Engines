package hw2;

// LLM usage disclosure:
// Kimi was used to assist with initial code generation for this assignment. 
// All generated code was tested and verified by hand through multiple test crawls before the final run.

import edu.uci.ics.crawler4j.crawler.Page;
import edu.uci.ics.crawler4j.crawler.WebCrawler;
import edu.uci.ics.crawler4j.parser.HtmlParseData;
import edu.uci.ics.crawler4j.url.WebURL;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.regex.Pattern;

public class FoxCrawler extends WebCrawler {

    // Skip obvious non-required file types by extension.
    // NOTE: doc/docx are ALLOWED by the assignment, so they are not filtered here.
    private static final Pattern FILTERS = Pattern.compile(
        ".*\\.(css|js|json|xml|rss|zip|gz|rar|7z|mp[34]|wav|avi|mov|wmv|webm|m3u8|exe|dmg|iso|apk"
        + "|woff2?|ttf|eot|txt|csv|xlsx?|pptx?)(\\?.*)?$");

    // Inside the site = host is www.foxnews.com, over http OR https.
    private static final Pattern INSIDE = Pattern.compile(
        "^https?://www\\.foxnews\\.com([:/?#].*)?$");

    private static final String FETCH = "fetch_" + Controller.SITE_NAME + ".csv";
    private static final String VISIT = "visit_" + Controller.SITE_NAME + ".csv";
    private static final String URLS  = "urls_"  + Controller.SITE_NAME + ".csv";

    // Files are opened ONCE (overwrite mode => no duplicated headers / stale data from test runs).
    private static final PrintWriter FETCH_W = open(FETCH, true);
    private static final PrintWriter VISIT_W = open(VISIT, true);
    private static final PrintWriter URLS_W  = open(URLS, false); // large file, flushed in bulk

    static {
        FETCH_W.println("URL,Status");
        VISIT_W.println("URL,Size(Bytes),Outlinks,Content-Type");
        URLS_W.println("URL,Indicator");
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            synchronized (URLS_W) { URLS_W.flush(); URLS_W.close(); }
            synchronized (FETCH_W) { FETCH_W.flush(); FETCH_W.close(); }
            synchronized (VISIT_W) { VISIT_W.flush(); VISIT_W.close(); }
        }));
    }

    private static PrintWriter open(String file, boolean autoFlush) {
        try {
            return new PrintWriter(new BufferedWriter(new FileWriter(file, false)), autoFlush);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private static void write(PrintWriter w, String line) {
        synchronized (w) {          // multiple crawler threads share these writers
            w.println(line);
        }
    }

    private static String csvSafe(String s) {
        return s.replace(",", "-");  // FAQ: replace comma with "-" or "_"
    }

    private static boolean isInside(String url) {
        return INSIDE.matcher(url.toLowerCase()).matches();
    }

    private static boolean allowedType(String ct) {
        if (ct == null) return false;
        return ct.equals("text/html")
            || ct.startsWith("image/")
            || ct.equals("application/pdf")
            || ct.equals("application/msword")
            || ct.equals("application/vnd.openxmlformats-officedocument.wordprocessingml.document");
    }

    // Decides whether to schedule a URL
    @Override
    public boolean shouldVisit(Page referringPage, WebURL url) {
        String href = url.getURL().toLowerCase();
        return isInside(href) && !FILTERS.matcher(href).matches();
    }

    // fetch_*.csv : every fetch attempt + its HTTP status code
    @Override
    protected void handlePageStatusCode(WebURL webUrl, int statusCode, String statusDescription) {
        write(FETCH_W, csvSafe(webUrl.getURL()) + "," + statusCode);
    }

    // visit_*.csv + urls_*.csv : successfully downloaded pages only
    @Override
    public void visit(Page page) {
        String contentType = page.getContentType();
        if (contentType != null) {
            contentType = contentType.split(";")[0].trim().toLowerCase(); // drop charset
        }
        if (!allowedType(contentType)) {
            return; // ignore css/js/json/video/...
        }

        int size = page.getContentData() == null ? 0 : page.getContentData().length;
        int outlinks = 0;

        if (page.getParseData() instanceof HtmlParseData) {
            HtmlParseData html = (HtmlParseData) page.getParseData();
            outlinks = html.getOutgoingUrls().size();
            // Log every extracted URL here so that
            // (# rows in urls.csv) == (sum of Outlinks column in visit.csv)
            for (WebURL out : html.getOutgoingUrls()) {
                write(URLS_W, csvSafe(out.getURL()) + "," + (isInside(out.getURL()) ? "OK" : "N_OK"));
            }
        }

        write(VISIT_W, csvSafe(page.getWebURL().getURL()) + "," + size + "," + outlinks + "," + contentType);
    }
}