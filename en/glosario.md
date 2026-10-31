# Glosario de la traducción inglesa

Traducción desde el español 1.0 (`75b82d8`), iniciada con el piloto del capítulo 5 y ampliada a los capítulos 1–4 y, después, 6–8. Inglés claro, ortografía estadounidense. Los términos conceptuales se mantienen estables; los rótulos citados reproducen cada interfaz inglesa, incluso cuando usa ortografía británica.

| Español | Inglés | Criterio |
|---|---|---|
| aptitud | fitness | No «aptitude». |
| selección de padres | parent selection | Distinguirla del reemplazo. |
| conjunto o pool de padres | parent pool | Copias de individuos existentes. |
| presión selectiva / de selección | selection pressure | Misma traducción en todo el capítulo. |
| explotación / exploración | exploitation / exploration | Conservar la distinción. |
| selección por torneo | tournament selection | Binary tournament cuando k = 2. |
| con / sin reemplazo | with / without replacement | Muestreo; distinto de replacement entre generaciones. |
| selección por ruleta | roulette-wheel selection | «Roulette» cuando es el rótulo abreviado de la herramienta. |
| aptitud proporcional | fitness-proportionate | Descriptor del mecanismo. |
| truncamiento | truncation selection | «Truncation» en controles. |
| selección por media | selection by mean fitness | No confundir con la mediana. |
| copias esperadas | expected copies | Esperanza, no resultado de una ejecución. |
| muestreo estocástico universal | stochastic universal sampling (SUS) | Mantener SUS. |
| toma de control | takeover / takeover time | Evento / número de generaciones. |
| deriva genética | genetic drift | Cambio por muestreo en población finita. |
| descendientes / hijos | offspring | En el contexto de operadores y la regla de Axelrod. |
| reemplazo | replacement | Operador que forma la siguiente población. |
| representación / codificación | representation / encoding | Representation para el concepto; encoding para la codificación concreta. |
| genotipo / fenotipo | genotype / phenotype | Cromosoma / solución representada. |
| válido / factible | valid / feasible | Validez de la representación / cumplimiento de restricciones; no intercambiarlos. |
| vecindad / vecino | neighborhood / neighbor | Ortografía estadounidense en prosa; conservar neighbour cuando es rótulo literal. |
| óptimo local / global | local / global optimum | Plural optima. |
| paisaje de aptitud / cuenca / meseta | fitness landscape / basin / plateau | Conservar la dependencia de representación y vecindad. |
| sembrar / solución sembrada | seed / seeded solution | No atribuir mejora garantizada al algoritmo completo. |
| aproximación determinista | deterministic approximation | Distinguir de esperanza exacta y media de ejecuciones. |
| función objetivo / aptitud | objective function / fitness | Distinguir valor original y transformación usada por selección. |
| violación / penalización / peso crítico | violation / penalty / critical weight | Conservar umbral, empate y desigualdad estricta. |
| mochila / asignación / viajante | knapsack / assignment / traveling salesman | TSP en rótulos cuando lo usa la interfaz. |
| muestreo por hipercubo latino | Latin hypercube sampling | Mayúscula Latin; no cambiar parámetros. |
| inhibición secuencial simple | simple sequential inhibition (SSI) | Mantener SSI y regla de distancia mínima. |
| caché / ruido / metamodelo | cache / noise / surrogate model | Meta-model cuando reproduce el rótulo de la herramienta. |
| variabilidad del muestreo | sampling variability | Rótulo «Sampling variability». |
| desviación típica | standard deviation | Mantener σ y su definición. |
| ejemplo reproducible | Reproducible Example | Conserva identificadores `.ejemplo`. |
| En la aplicación | In the Application | Conserva `.en-app`. |
| ejercicio / solución | Exercise / solution | Soluciones plegadas en HTML. |
| Básico / Avanzado / Para saber más | Basic / Advanced / Further reading | Conserva colores y clases. |
| Padre 1 / Hijo 1 | Parent 1 / Child 1 | Nombres de la herramienta; offspring en prosa general. |
| cruce (recombinación) | crossover (recombination) | Título del capítulo 6: «Crossover». |
| heredabilidad / validez | heritability / validity | Condiciones del cruce (Talbi). |
| máscara de cruce | crossover mask | Un bit por posición. |
| probabilidad de cruce | crossover probability *Pc* | Conservar *Pc*. |
| tramo / segmento | stretch / segment | «Stretches» es la columna de crossover-ga. |
| cruce de orden / de ciclos | order crossover (OX) / cycle crossover (CX) | PMX: partially mapped crossover. |
| tabla de correspondencias dirigida | directed mapping table | PMX en la herramienta. |
| dar la vuelta (OX) | wrap around | NWOX: non-wrapping order crossover. |
| aristas / adyacencias / precedencias | edges / adjacencies / precedences | Con o sin sentido: directed / undirected. |
| puro / respetuoso | pure / respectful | Propiedades de Talbi. |
| sesgo del cruce | crossover bias | Pavai y Geetha. |
| inversión de bits | bit-flip mutation | No confundir con inversion (permutaciones). |
| reinicio aleatorio / deslizamiento | random resetting / creep mutation | Paso máximo: maximum step *s*. |
| tamaño de paso | step size | σ en la mutación gaussiana. |
| intercambio / inserción / inversión / mezcla | swap / insertion / inversion / scramble | Rótulos: Swap, Insert, Inversion, Scramble mutation. |
| alelo aleatorio | random allele | Variante de bit-flip. |
| ergodicidad / localidad | ergodicity / locality | Talbi, p. 209. |
| reemplazo / selección de supervivientes | replacement / survivor selection | Distinto de «with replacement» en el muestreo. |
| reemplazo generacional / estado estacionario | generational replacement / steady-state replacement | Rótulo: «Steady state». |
| élite / elitismo débil | elite / weak elitism | Elite size *e*. |
| salto generacional | generation gap | *G*. |
| apiñamiento (determinista) | (deterministic) crowding | Factor de apiñamiento: crowding factor *CF*. |
| criterio de parada | stopping criterion | «k generations without improvement». |
| estrategias evolutivas | evolution strategies | (μ + λ), (μ, λ). |

## Controles de selection-ga

| Español | Inglés de la interfaz |
|---|---|
| Sortear de nuevo | Draw again |
| Copias en 1000 repeticiones | Copies in 1000 repetitions |
| Desplazamiento C | Shift C |
| Introducir las aptitudes a mano | Enter the fitness values manually |
| Ejemplo de Goldberg (x²) | Goldberg’s example (x²) |
| Practicar | Practice |
| Comparar mecanismos | Compare mechanisms |
| Varias generaciones solo con selección | Several generations of selection only |
| Simular de nuevo | Simulate again |
| Aptitud media | Mean fitness |
| El mejor se pierde | The best is lost |
| Presión y diversidad en 1000 repeticiones | Pressure and diversity in 1000 repetitions |

Fuente de rótulos: `js/i18n.js` y contenidos de selection-ga; el informe del piloto distingue inspección de fuentes y comportamiento comprobado. SelectionMechanisms conserva su enlace existente; no se inventa un parámetro de idioma para ella.

## Rótulos de los capítulos 1–4

Los controles y títulos se cotejan con `registry.js`, `i18n.js` y contenidos de
representation-ga e initialization-and-evaluation-ga. Ejemplos de diferencias
que se conservan: **TSP · permutation**, **2D function · bit string**,
**Feasible initialisation**, **The cost of evaluating**, **Roulette wheel**,
**Penalty weight λ** y **Several objectives**. La prosa sigue usando initialization
y traveling, según el criterio estadounidense. La lectura de estas fuentes se
registra separadamente de las actividades ejecutadas y de su prueba pública.

## Rótulos de los capítulos 6–8

Cotejados con `i18n.js`, `registry.js` y `content/*.js` de crossover-ga,
mutation-ga y selection-ga (clones de `main` del 2026-10-31) y, para una muestra,
con las interfaces publicadas con `lang=en`. Ejemplos: **Classic (Goldberg, 1989)**,
**Order from the start**, **Left to right (NWOX, Cicirello, 2006)**, **Random cycles**,
**Show as routes**, **Enter parents manually**, **Swap probability (p)**, **Weight (λ)**,
**Average over** (crossover-ga) frente a **Average with** (mutation-ga), **Copy of a parent**
frente a **Copy of the parent**, **Creep mutation**, **Clamp at the bounds**, **Wrap around**,
**Maximum step s**, **Generational with elitism**, **Elite size e**, **Steady state**,
**Replace the worst if better**, **Number of offspring λ**, **Random population**,
**Survives** y **Age**. crossover-ga usa ortografía británica en algunos textos
(*neighbours*, *travelling*); la prosa sigue la estadounidense.
