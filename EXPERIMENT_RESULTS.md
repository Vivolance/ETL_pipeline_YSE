## Prototype 1 - Traverse HTML document with BS4 recursively

Pros:
- Good enough to extract search result text (but not the structure and urls) correctly
- No machine learning required.

Cons
- Unable to group search results, urls, header correctly
- Results from API is different from what we see on the browser (Yahoo returns different results for API call vs UI)

```commandline
PYTHONPATH=. python src/prototypes/prototype_one_recursive_bs4.py
```

### Lessons Learnt:
- Due to yahoo returning different results to API call compared to UI, we can't approach this with the NLP route
- We need to present this problem in the form of screenshot capturing, and extraction of data from screenshots
- That said, Prototype 1 is somewhat sufficient for us to move on with the ETL pipeline
- We can repackage Prototype 1 to extract text from the search results, to perform sentiment analysis on
- This can be useful for stock sentiment analysis

### Possible Paths:
1. (Recommended) Repackage Prototype 1 into a Stock sentiment analysis search engine
2. Continue with Yahoo Search Engine Problem Statement, but use Selenium + Screenshots + Convolutional Neural Networks to extract and organize search results
