import numpy as np

def clustering(data, algo: str, *args, **kwargs):
    algo = algo.lower()
    if algo == "dbscan":
        from sklearn.cluster import DBSCAN
        # eps=0.5, min_samples=5
        dbscan = DBSCAN(*args, **kwargs)
        dbscan.fit(data)
        return dbscan.labels_
    raise ValueError("Unknown clustering algorithm: {}".format(algo))

if __name__ == '__main__':
    # test_cases = [
    #     ['deepface', ['yolov8']],
    # ]
    # for test_case in test_cases:
    #     print("-- Testing {}".format(test_case[0]))
    #     print("     Creating with args:", test_case[1])
    #     detector = create_detector(test_case[0], *test_case[1])
    #     print("detector", detector)
    #     embeddings = detector.get_face_embedding(image_path = 'test_data/ycy.jpg')
    #     embeddings = np.array(embeddings[0]["embedding"])
    #     print("embeddings", embeddings.shape)

    face_embedding_test_data = np.load("face_embedding_test_data.npy", allow_pickle=True)
    print("Count of images:", len(face_embedding_test_data))
    embeds = []
    for data in face_embedding_test_data:
        embeds += ([ face["embedding"] for face in data["faces"] ])
    print("Count of faces:", len(embeds))
    embeds = np.array(embeds)
    print("Embedding shape: ", embeds.shape)
    embeds = embeds / np.linalg.norm(embeds, axis=1)[:, np.newaxis]
    # clustering
    labels = clustering(embeds, "dbscan", eps=0.5, min_samples=4)
    print("Labels:", labels)
    print("Number of categories:", len(set(labels)) - (-1 in labels))

