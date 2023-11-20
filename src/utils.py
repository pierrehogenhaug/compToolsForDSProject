def add_nodes_from_user_data(G, user_data):
    """
    Add nodes to the graph from user data.

    Parameters:
    - G (networkx.Graph): The graph to add nodes to.
    - user_data (pandas.DataFrame): The user data containing the 'Id' column.

    Returns:
    None
    """
    for user_id in user_data['Id']:
        G.add_node(user_id)


def add_edges_from_post_data(G, posts_data):
    """
    Add edges to a graph based on post data.

    Parameters:
    - G (networkx.Graph): The graph to add edges to.
    - posts_data (pandas.DataFrame): The post data containing information about posts.

    Returns:
    None
    """
    # Filter to only answers and drop NaNs
    answers_data = posts_data[posts_data['PostTypeId'] == 2].dropna(subset=['ParentId', 'OwnerUserId'])

    # Create a lookup table for question askers
    question_askers = posts_data[posts_data['PostTypeId'] == 1].set_index('Id')['OwnerUserId']

    # Iterate through answers
    for answerer_id, question_id in zip(answers_data['OwnerUserId'], answers_data['ParentId']):
        asker_id = question_askers.get(question_id)
        if asker_id is not None:
            G.add_edge(answerer_id, asker_id)


def add_edges_from_comment_data(G, comments_data, posts_data):
    """
    Add edges to the graph `G` based on the comment data.

    Parameters:
    - G (networkx.Graph): The graph to add edges to.
    - comments_data (pandas.DataFrame): The comment data containing 'UserId' and 'PostId' columns.
    - posts_data (pandas.DataFrame): The post data containing 'Id' and 'OwnerUserId' columns.

    Returns:
    None
    """
    # Drop NaNs
    comments_data = comments_data.dropna(subset=['PostId', 'UserId'])

    # Create a lookup table for post owners
    post_owners = posts_data.set_index('Id')['OwnerUserId']

    # Iterate through comments
    for commenter_id, post_id in zip(comments_data['UserId'], comments_data['PostId']):
        post_owner_id = post_owners.get(post_id)
        if post_owner_id is not None:
            G.add_edge(commenter_id, post_owner_id)
