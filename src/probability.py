class AnalizadorProbabilidades:
    def __init__(self, datos_home_away, datos_lesiones):
        self.home_away = self._procesar_home_away(datos_home_away)
        self.lesiones = self._procesar_lesiones(datos_lesiones)
    
    def _procesar_home_away(self, datos_home_away):
        equipos = {}
        for equipo_data in datos_home_away:
            nombre_equipo = equipo_data['squad']
            equipos[nombre_equipo] = {
                'home': equipo_data['home'],
                'away': equipo_data['away']
            }
        return equipos
    
    def _procesar_lesiones(self, datos_lesiones):
        if datos_lesiones.get('status') == 'success':
            return datos_lesiones['data']
        return []
    
    def _calcular_prob_victoria_local(self, stats_local, stats_visitante):
        pts_local_home = float(stats_local['points_per_game'])
        pts_visitante_away = float(stats_visitante['points_per_game'])
        factor_pts = pts_local_home / (pts_local_home + pts_visitante_away + 0.1)
        
        xg_diff_local = float(stats_local['expected_goal_difference_per_game'])
        xg_diff_visitante = float(stats_visitante['expected_goal_difference_per_game'])
        factor_xg = 0.5 + (xg_diff_local - xg_diff_visitante) * 0.05
        
        prob_base = (factor_pts * 0.6) + (factor_xg * 0.4)
        
        return max(0.2, min(0.8, prob_base))
    
    def _calcular_prob_victoria_visitante(self, stats_local, stats_visitante):
        pts_local_home = float(stats_local['points_per_game'])
        pts_visitante_away = float(stats_visitante['points_per_game'])
        factor_pts = pts_visitante_away / (pts_local_home + pts_visitante_away + 0.1)
        
        xg_diff_local = float(stats_local['expected_goal_difference_per_game'])
        xg_diff_visitante = float(stats_visitante['expected_goal_difference_per_game'])
        factor_xg = 0.5 + (xg_diff_visitante - xg_diff_local) * 0.05
        
        prob_base = (factor_pts * 0.6) + (factor_xg * 0.4)
        
        return max(0.1, min(0.6, prob_base))
    
    def _calcular_ventaja_local(self, stats_local, stats_visitante):
        ventaja_xg = float(stats_local['expected_goal_difference_per_game']) - float(stats_visitante['expected_goal_difference_per_game'])
        ventaja_pts = float(stats_local['points_per_game']) - float(stats_visitante['points_per_game'])
        
        ventaja_base = 1.3
        ventaja_adicional = (ventaja_xg * 0.1) + (ventaja_pts * 0.05)
        
        return min(ventaja_base + ventaja_adicional, 1.6)
    
    def _calcular_impacto_lesiones(self, equipo_local, equipo_visitante):
        impacto = {'factor_local': 1.0, 'factor_visitante': 1.0}
        
        lesiones_local = [l for l in self.lesiones if l['team'] == equipo_local]
        for lesion in lesiones_local:
            importancia = self._evaluar_importancia_jugador(lesion)
            if lesion['position'] in ['F', 'M']:
                impacto['factor_local'] *= (1 - importancia * 0.15)
            elif lesion['position'] in ['D', 'G']:
                impacto['factor_local'] *= (1 - importancia * 0.10)
        
        lesiones_visitante = [l for l in self.lesiones if l['team'] == equipo_visitante]
        for lesion in lesiones_visitante:
            importancia = self._evaluar_importancia_jugador(lesion)
            if lesion['position'] in ['F', 'M']:
                impacto['factor_visitante'] *= (1 - importancia * 0.15)
            elif lesion['position'] in ['D', 'G']:
                impacto['factor_visitante'] *= (1 - importancia * 0.10)
        
        impacto['factor_local'] = max(0.7, impacto['factor_local'])
        impacto['factor_visitante'] = max(0.7, impacto['factor_visitante'])
        
        return impacto
    
    def _evaluar_importancia_jugador(self, lesion):
        importancia = 0.5
        
        try:
            partidos = int(lesion['matches']) if lesion['matches'] != '-' else 0
            if partidos > 8:
                importancia += 0.3
            elif partidos > 5:
                importancia += 0.2
            elif partidos > 2:
                importancia += 0.1
        except:
            pass
        
        try:
            goles = int(lesion['goals']) if lesion['goals'] != '-' else 0
            asistencias = int(lesion['assists']) if lesion['assists'] != '-' else 0
            if goles + asistencias > 5:
                importancia += 0.2
            elif goles + asistencias > 2:
                importancia += 0.1
        except:
            pass
        
        if 'inj-type injury-plus' in lesion['type']:
            importancia += 0.2
        
        return min(importancia, 1.0)
    
    def _normalizar_probabilidades(self, prob_local, prob_empate, prob_visitante):
        total = prob_local + prob_empate + prob_visitante
        if total == 0:
            return {'local': 0.33, 'empate': 0.34, 'visitante': 0.33}
        
        return {
            'local': prob_local / total,
            'empate': prob_empate / total,
            'visitante': prob_visitante / total
        }
    
    def predecir_partido(self, equipo_local, equipo_visitante):
        if equipo_local not in self.home_away:
            raise ValueError(f"Home team '{equipo_local}' not found in dataset.")
        if equipo_visitante not in self.home_away:
            raise ValueError(f"Away team '{equipo_visitante}' not found in dataset.")
        
        stats_local = self.home_away[equipo_local]['home']
        stats_visitante = self.home_away[equipo_visitante]['away']
        
        ventaja_local = self._calcular_ventaja_local(stats_local, stats_visitante)
        
        impacto_lesiones = self._calcular_impacto_lesiones(equipo_local, equipo_visitante)
        
        prob_victoria_local = self._calcular_prob_victoria_local(stats_local, stats_visitante)
        prob_victoria_visitante = self._calcular_prob_victoria_visitante(stats_local, stats_visitante)
        prob_empate = 1 - (prob_victoria_local + prob_victoria_visitante)
        
        prob_victoria_local *= ventaja_local * impacto_lesiones['factor_local']
        prob_victoria_visitante *= impacto_lesiones['factor_visitante']
        
        prob_empate = max(0.1, prob_empate)
        
        return self._normalizar_probabilidades(prob_victoria_local, prob_empate, prob_victoria_visitante)
