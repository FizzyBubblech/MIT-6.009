# NO IMPORTS ALLOWED!

import json

BACON = 4724

def did_x_and_y_act_together(data, actor_id_1, actor_id_2):
    '''
    Determine whether two actors acted together in the same film.
    
    Arguments:
        data: the database to be used (a list of records of actors who have acted together 
              in a film, as well as a film ID: [actor_id_1, actor_id_2, film_id])
        actor_id_1, actor_id_2: IDs representing actors(int)
        
    Returns:
        True if the two given actors ever acted together in a film, 
        and False otherwise.
    '''
    for record in data:
        if actor_id_1 in record and actor_id_2 in record:
            return True
    return False

def get_acted_with_map(data):
    '''Map each actor to a set of actors acted with'''
    acted_with = {}
    for act1, act2, _ in data:
        # doesn't add actors acting with themselves to the set
        if act1 == act2:
            continue
        acted_with.setdefault(act1, set()).add(act2)
        acted_with.setdefault(act2, set()).add(act1)
    return acted_with

def expand_level(acted_with, current_bacon_level, parents):
    '''Get the Bacon number i+1 actors from the Bacon number i actors.'''
    next_bacon_level = set()
    # map childs to parent actors and add them to next level
    for actor in current_bacon_level:
        for child in acted_with[actor]:
            # ignore previous level actors
            if child not in parents:
                parents[child] = actor
                next_bacon_level.add(child)
    return next_bacon_level
 
def get_actors_with_bacon_number(data, n):
    '''
    Get all actors with given Bacon number from the data database.
    
    Arguments:
        data: the database to be used (a list of records of actors who have acted together 
              in a film, as well as a film ID: [actor_id_1, actor_id_2, film_id])
        n: the Bacon number(int)
        
    Returns:
        A list containing the ID numbers of all the actors with n Bacon number.
    '''
    acted_with = get_acted_with_map(data)
    # initialize dictionaries - the first level(starting with Bacon) 
    # and parents with root Bacon
    bacon_level = {BACON}
    parents = {BACON:None}
    # iterate to the n bacon level
    for i in range(n):
        bacon_level = expand_level(acted_with, bacon_level, parents)
    return list(bacon_level)
 
def get_bacon_path(data, actor_id):
    '''
    Get "Bacon path" from Kevin Bacon to the given actor ID.
    
    Arguments:
        data: the database to be used (a list of records of actors who have acted together 
              in a film, as well as a film ID: [actor_id_1, actor_id_2, film_id])
        actor_id: an ID representing an actor(int)
    
    Returns:
        a list of actor IDs (any such shortest list, if there are several) detailing a "Bacon path" 
        from Kevin Bacon to the actor denoted by actor_id. If no path exists, return None.
    '''
    return get_path(data, BACON, actor_id)

def find_path(parents, actor_id):
    '''
    Returns a path from root(no parents) actor of given parents dictionary to given 
    actor_id actor 
    '''
    result = []
    # construct the path until the root is reached
    while actor_id != None:
        result.append(actor_id)
        actor_id = parents[actor_id]
    # reverse it because started from the end
    result.reverse()
    return result

def get_path(data, actor_id_1, actor_id_2):
    '''
    Get path from one given actor to the other.
    
    Arguments:
        data: the database to be used (a list of records of actors who have acted together 
              in a film, as well as a film ID: [actor_id_1, actor_id_2, film_id])
        actor_id_1, actor_id_2: IDs representing actors(int)
        
    Returns:
        a list of actor IDs (any such shortest list, if there are several) detailing 
        a path from actor_id_1 actor to the actor_id_2 actor. If no path exists, return None.
    '''
    acted_with = get_acted_with_map(data)
    # return None if path doesn't exist
    if (actor_id_1 not in acted_with) or (actor_id_2 not in acted_with):
        return None
    # initialize first level with actor_id_1 and parents with same root
    bacon_level = {actor_id_1}
    parents = {actor_id_1:None}
    # iterate till actor_2 is found
    while actor_id_2 not in bacon_level:
        bacon_level = expand_level(acted_with, bacon_level, parents)
    path = find_path(parents, actor_id_2)
    return path

def get_namesdb():
    '''Returns a mapping from actor names to IDs'''
    with open('resources/names.json') as f:
        namesdb = json.load(f)
    return namesdb

def get_moviesdb():
    ''' Returns a mapping from movie names to IDs'''
    with open('resources/movies.json') as f:
        moviesdb = json.load(f)
    return moviesdb

def get_id_to_movie_map(moviesdb):
    '''Returns a mapping from movie IDs to names'''
    result = {}
    for k,v in moviesdb.items():
        result[v] = k
    return result

def get_actors_to_movie_map(data):
    '''Returns a mapping from actor pairs to movies acted together in'''
    result = {}
    for a1, a2, m in data:
        result[frozenset({a1, a2})] = m
    return result

def get_movie_path(data, actor_1, actor_2):
    '''
    Get movie path from one actor to another.
    
    Arguments:
        data: the database to be used (a list of records of actors who have acted together 
              in a film, as well as a film ID: [actor_id_1, actor_id_2, film_id])
        actor_1, actor_2: actor names(str), must be in data
        
    Returns:
        a list of movie names (any such shortest list, if there are several) detailing 
        a path from actor_1 actor to the actor_2 actor.
    '''
    #convert actor names to id and get actor path
    namesdb = get_namesdb()
    path = get_path(data, namesdb[actor_1], namesdb[actor_2])
    # initialize dictionaries to find movie path
    id_movie = get_id_to_movie_map(get_moviesdb())
    actors_movie = get_actors_to_movie_map(data)
    # find movie path by looking up movie ids with actor pairs
    # and then convert movie id to name
    movie_path = []
    for i in range(len(path)-1):
        movie_id = actors_movie[frozenset({path[i], path[i+1]})]
        movie_path.append(id_movie[movie_id])
    return movie_path
    

if __name__ == '__main__':
    with open('resources/tiny.json') as f:
        smalldb = json.load(f)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass
