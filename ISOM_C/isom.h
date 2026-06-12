#ifndef ISOM_H
#define ISOM_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NAME 50
#define MAX_ARGS 20
#define MAX_EDGES 10000
#define MAX_UNIQUE 50000

typedef struct {
    char pred[MAX_NAME];
    char args[MAX_ARGS][MAX_NAME];
    int arity;
} Hyperedge;

typedef struct {
    Hyperedge edges[MAX_EDGES];
    int edge_count;
    int arity;
} Hypergraph;

typedef struct {
    char from[MAX_NAME];
    char to[MAX_NAME];
} Sub;

typedef struct {
    Sub* subs;
    int count;
    int capacity;
} Unifier;

Hypergraph* parse_hypergraph(const char* string);
void free_hypergraph(Hypergraph* graph);
void print_hypergraph(Hypergraph* graph);

Unifier* check_isomorphism(Hypergraph* graph1, Hypergraph* graph2);
void unifier_free(Unifier* unifier);

#endif
