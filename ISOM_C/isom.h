#ifndef ISOM_H
#define ISOM_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NAME 50
#define MAX_ARGS 20
#define MAX_UNIQUE 500000
#define EDGE_INIT_CAPACITY 1024

// A single atomic formula: pred(args[0], ..., args[arity-1])
typedef struct {
    char pred[MAX_NAME];
    char args[MAX_ARGS][MAX_NAME];
    int arity;
} Hyperedge;

// An elementary conjunction of atomic formulas
typedef struct {
    Hyperedge* edges;
    int edge_count;
    int edge_capacity;
    int max_arity;
} Hypergraph;

// A substitution pair: replace `from` with `to`
typedef struct {
    char from[MAX_NAME];
    char to[MAX_NAME];
} Sub;

// A unifier — set of substitutions (bijection of variables to constants)
typedef struct {
    Sub* subs;
    int count;
    int capacity;
} Unifier;

// Parse a string like "p(a,b)&q(c,d)" into a Hypergraph
Hypergraph* parse_hypergraph(const char* string);

// Free a Hypergraph allocated by parse_hypergraph
void free_hypergraph(Hypergraph* graph);

// Print a Hypergraph in human-readable form
void print_hypergraph(Hypergraph* graph);

// Check isomorphism of two hypergraphs.
// Returns one possible unifier (from graph1 constants to graph2 args)
// or NULL if not isomorphic.
Unifier* check_isomorphism(Hypergraph* graph1, Hypergraph* graph2);

// Free a unifier returned by check_isomorphism
void unifier_free(Unifier* unifier);

// Print a unifier as "from -> to" lines
void print_unifier(Unifier* unifier);

#endif
