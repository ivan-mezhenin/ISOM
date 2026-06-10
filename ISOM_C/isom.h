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
    int edge_cnt;
    int arity;
} Hypergraph;

typedef struct {
    char var[MAX_NAME];
    char val[MAX_NAME];
} Sub;

typedef struct {
    Sub* subs;
    int cnt;
    int cap;
} Unifier;

// Функции
Hypergraph* parse_hg(const char* str);
void free_hg(Hypergraph* g);
void print_hg(Hypergraph* g);

// Главная функция: возвращает ОДИН унификатор (или NULL, если не изоморфны)
Unifier* check_iso(Hypergraph* g1, Hypergraph* g2);
void uni_free(Unifier* u);

#endif
