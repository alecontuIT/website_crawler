from web_crawler import WebCrawler

def main():
    print("Starting the Web Crawler!")
    print("With this program you can crawl a website (like a blog) and get all the links of the pages inside the website.")
    home_url = str(input("Please enter the URL of the website you want to crawl, please provide the whole URL e.g. 'https://waitbutwhy.com/': "))
    print("-----------------------------------")
    print("The program can also use the LLM algorithm to summarize the content of the pages or optimize the SEO of the website.")
    print("To do so, you need to provide the LLM algorithm with the API key in the llm_api.txt file.")
    print("Remember that the LLM algorithm is a freemium service, so you need to have an account and an API key.")
    print("You have max 10 free request per minute and it will take some time to get the results.")
    llm = input("Do you want to use the LLM algorithm? (True/False): ")
    if llm=='True'or llm=='true' or llm=='T' or llm=='t':
        llm = True
        llm_kind = str(input("Which kind of LLM algorithm do you want to use? (summarizer/seo_optimizer): "))
    else:
        llm = False
        llm_kind = None
        print("Ok, he program will use the default algorithm without LLM call.")
    print("-----------------------------------")
    print("The program will start crawling the website now.")
    wc = WebCrawler(home_url, llm=llm, llm_kind=llm_kind)
    wc.start_scraping()
    print("The program has finished crawling the website.")
    print("-----------------------------------")
    print("Now it will save the results in the results folder.")
    wc.save_results()
    print("The results have been saved.")
    print("-----------------------------------")
    print("The program will now plot the results.")
    wc.plot()
    print("Thank you for using the Web Crawler!")
    print("Goodbye!")


if __name__ == "__main__":
    main()