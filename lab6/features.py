

def extract(stack, queue, state, feature_names, sentence):
    features = []
    features.append(stack[0]["form"])
    features.append(stack[0]["postag"])
    features.append(queue[0]["form"])
    features.append(queue[0]["postag"])
    return features
