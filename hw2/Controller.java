package hw2;

// LLM usage disclosure:
// Kimi was used to assist with initial code generation for this assignment. 
// All generated code was tested and verified by hand through multiple test crawls before the final run.

import edu.uci.ics.crawler4j.crawler.CrawlConfig;
import edu.uci.ics.crawler4j.crawler.CrawlController;
import edu.uci.ics.crawler4j.fetcher.PageFetcher;
import edu.uci.ics.crawler4j.robotstxt.RobotstxtConfig;
import edu.uci.ics.crawler4j.robotstxt.RobotstxtServer;

public class Controller {
    public static final String SITE_NAME = "foxnews";
    public static final String SEED = "https://www.foxnews.com/";

    public static void main(String[] args) throws Exception {
        CrawlConfig config = new CrawlConfig();
        config.setCrawlStorageFolder("crawl_data");       
        config.setMaxPagesToFetch(10000);                 
        config.setMaxDepthOfCrawling(16);
        config.setPolitenessDelay(2500);                  
        config.setIncludeBinaryContentInCrawling(true);   
        config.setIncludeHttpsPages(true);
        config.setUserAgentString("Mozilla/5.0 (compatible; USC-CSCI572-HW2-Bot/1.0)");

        PageFetcher pageFetcher = new PageFetcher(config);
        RobotstxtConfig robotstxtConfig = new RobotstxtConfig();
        RobotstxtServer robotstxtServer = new RobotstxtServer(robotstxtConfig, pageFetcher);
        CrawlController controller = new CrawlController(config, pageFetcher, robotstxtServer);

        controller.addSeed(SEED);

        int numberOfCrawlers = 7;   
        controller.start(FoxCrawler.class, numberOfCrawlers);
        System.out.println("=== CRAWL DONE ===");
    }
}