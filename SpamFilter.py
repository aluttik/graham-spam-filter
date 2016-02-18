from collections import Counter
from aima.utils import DefaultDict, product as prod
import re

class SpamFilter:
    sep = re.compile(r"[^a-z0-9-'\$]", re.MULTILINE)

    config = {'word_occurance_threshold': 5,
              'default_probability': 0.4,
              'probability_threshold': 0.9,
              'nonspam_importance_ratio': 2,
              'unique_tokens': False,
              'learning': False}

    def __init__(self, nonspam_corpus, spam_corpus, **kwargs):
        self.config.update(kwargs)
        self.nonspam_corpus = nonspam_corpus
        self.spam_corpus = spam_corpus
        self.probabilities = DefaultDict(self.config['default_probability'])
        self.update()

    def _tokenize(self, message):
        valid_token = lambda x: x and not unicode(x).isnumeric()
        return filter(valid_token, re.split(self.sep, message.lower()))

    def update(self):
        self.probabilities.clear()
        good = Counter(self._tokenize(' '.join(self.nonspam_corpus)))
        bad = Counter(self._tokenize(' '.join(self.spam_corpus)))
        for word in good | bad:
            g = float(good[word] * self.config['nonspam_importance_ratio'])
            b = float(bad[word])
            if g + b >= self.config['word_occurance_threshold']:
                if word in good and word in bad:
                    p = min(1.0, b / len(self.spam_corpus))
                    n = min(1.0, g / len(self.nonspam_corpus))
                    self.probabilities[word] = p / (p + n)
                else:
                    self.probabilities[word] = 0.01 if word in good else 0.99

    def is_spam(self, message):
        self.update()
        tokens = self._tokenize(message)
        if self.config['unique_tokens']:
            tokens = list(set(tokens))
        interesting = lambda x: abs(0.5 - self.probabilities[x])
        tokens = sorted(tokens, key=interesting, reverse=True)[:15]
        probs = [self.probabilities[x] for x in tokens]
        combined = prod(probs) / (prod(probs) + prod(1 - x for x in probs))
        result = combined >= self.config['probability_threshold']
        if self.config['learning']:
            corpus = self.spam_corpus if result else self.nonspam_corpus
            corpus.append(message)
            self.update()
        return result


if __name__ == '__main__':
    spam_corpus = ["I am spam, spam I am.", "I do not like that Spamiam."]
    ham_corpus = ["Do I like green eggs and ham?", "I do."]

    spam_filter = SpamFilter(ham_corpus, spam_corpus)
    spam_filter.config['word_occurance_threshold'] = 1

    assert (spam_filter.is_spam("do ham like spam do spam") == True)
    assert (spam_filter.is_spam("do ham like spam do spam like") == False)

    print 'Tests Passed'
