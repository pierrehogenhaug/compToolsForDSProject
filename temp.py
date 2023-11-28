def add_nodes_from_user_data(G, user_data):
    """
    Add nodes to the graph from user data, including attributes.

    Parameters:
    - G (networkx.Graph): The graph to add nodes to.
    - user_data (pandas.DataFrame): The user data containing the 'Id' column and other attributes.

    Returns:
    None
    """
    for _, row in user_data.iterrows():
        node_attributes = row.to_dict()
        user_id = node_attributes.pop('Id')  # Remove the 'Id' as it will be the node identifier
        G.add_node(user_id, **node_attributes)
        

def add_edges_from_post_data(G, posts_data):
    """
    Add edges to the graph based on post data.

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
        # Check that answerer and asker are not the same
        if asker_id is not None and answerer_id != asker_id:
            G.add_edge(answerer_id, asker_id)


def add_edges_from_comment_data(G, comments_data, posts_data):
    """
    Adds edges to the graph `G` based on the comment data.

    Parameters:
        G (networkx.Graph): The graph to which the edges will be added.
        comments_data (pandas.DataFrame): The comment data containing 'UserId' and 'PostId' columns.
        posts_data (pandas.DataFrame): The post data containing 'Id' and 'OwnerUserId' columns.

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
        # Check that commenter and post owner are not the same
        if post_owner_id is not None and commenter_id != post_owner_id:
            G.add_edge(commenter_id, post_owner_id)


def preprocess_user_data(user_data, posts_data, comments_data, threshold):
    """
    Preprocesses user data by calculating the number of posts and comments per user,
    combining the counts, and filtering out users who do not meet the threshold.
    
    Args:
        user_data (DataFrame): DataFrame containing user data.
        posts_data (DataFrame): DataFrame containing posts data.
        comments_data (DataFrame): DataFrame containing comments data.
        threshold (int): Minimum count threshold for users to be considered active.
    
    Returns:
        DataFrame: DataFrame containing only the data of active users.
    """
    # Calculate the number of posts per user
    posts_count = posts_data['OwnerUserId'].value_counts()
    
    # Calculate the number of comments per user
    comments_count = comments_data['UserId'].value_counts()
    
    # Combine the counts, filling in zeros for users who haven't posted or commented
    combined_count = posts_count.add(comments_count, fill_value=0)
    
    # Filter users who meet the threshold
    active_users = combined_count[combined_count >= threshold].index
    
    # Filter the user_data DataFrame to include only active users
    active_user_data = user_data[user_data['Id'].isin(active_users)]
    
    return active_user_data


def preprocess_post_data(posts_data, active_user_data):
    """
    Preprocesses the post data by filtering it to only include posts owned by active users.

    Parameters:
    posts_data (DataFrame): The dataframe containing all the post data.
    active_user_data (DataFrame): The dataframe containing the data of active users.

    Returns:
    DataFrame: The filtered dataframe containing only the posts owned by active users.
    """
    active_posts_data = posts_data[posts_data['OwnerUserId'].isin(active_user_data['Id'])]
    
    return active_posts_data


def preprocess_comment_data(comments_data, active_user_data, active_posts_data):
    """
    Preprocesses comment data by filtering it to only include comments owned by active users
    and comments on posts by active users.

    Parameters:
    comments_data (DataFrame): The original comment data.
    active_user_data (DataFrame): The data of active users.
    active_posts_data (DataFrame): The data of active posts.

    Returns:
    DataFrame: The preprocessed comment data.
    """
    # Filter comments to only those owned by active users
    active_comments_data = comments_data[comments_data['UserId'].isin(active_user_data['Id'])]
    
    # Filter comments to only those on posts by active users
    active_comments_data = active_comments_data[active_comments_data['PostId'].isin(active_posts_data['Id'])]
    
    return active_comments_data


def convert_timestamps_to_strings(G):
    """
    Converts timestamps in the graph G to strings.

    Parameters:
    - G (networkx.Graph): The graph to convert timestamps in.

    Returns:
    - None
    """
    for node, data in G.nodes(data=True):
        for key, value in data.items():
            if isinstance(value, pd.Timestamp):
                # Convert Timestamp to string
                G.nodes[node][key] = value.strftime('%Y-%m-%d %H:%M:%S')

    for u, v, data in G.edges(data=True):
        for key, value in data.items():
            if isinstance(value, pd.Timestamp):
                # Convert Timestamp to string
                G.edges[u, v][key] = value.strftime('%Y-%m-%d %H:%M:%S')
