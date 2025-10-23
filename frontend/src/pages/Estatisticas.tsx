import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface ModalidadeStats {
  modalidade_nome: string;
  quantidade: number;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Estatisticas() {
  const [stats, setStats] = useState<ModalidadeStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simular carregamento de dados
    setTimeout(() => {
      setStats([
        { modalidade_nome: "Pregão - Eletrônico", quantidade: 3 },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  const totalContratacoes = stats.reduce((sum, item) => sum + item.quantidade, 0);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Estatísticas</h1>
          <p className="text-muted-foreground mt-2">
            Análise e visualização dos dados de contratações
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Distribuição por Modalidade</CardTitle>
              <CardDescription>
                Total de {totalContratacoes} contratação(ões)
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="h-[300px] flex items-center justify-center">
                  <div className="h-32 w-32 animate-pulse rounded-full bg-muted" />
                </div>
              ) : stats.length === 0 ? (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  Nenhum dado disponível
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={stats}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ modalidade_nome, percent }) =>
                        `${modalidade_nome}: ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="quantidade"
                    >
                      {stats.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Detalhamento por Modalidade</CardTitle>
              <CardDescription>
                Quantidade de contratações por tipo
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-12 animate-pulse rounded bg-muted" />
                  ))}
                </div>
              ) : stats.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  Nenhum dado disponível
                </div>
              ) : (
                <div className="space-y-4">
                  {stats.map((item, index) => (
                    <div key={item.modalidade_nome} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className="h-4 w-4 rounded-full"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="text-sm font-medium">{item.modalidade_nome}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-muted-foreground">
                          {item.quantidade} contratação(ões)
                        </span>
                        <span className="text-sm font-semibold">
                          {((item.quantidade / totalContratacoes) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Informações Gerais</CardTitle>
            <CardDescription>
              Resumo dos dados coletados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">
                  Total de Contratações
                </p>
                <p className="text-2xl font-bold">{totalContratacoes}</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">
                  Modalidades Diferentes
                </p>
                <p className="text-2xl font-bold">{stats.length}</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">
                  Modalidade Mais Comum
                </p>
                <p className="text-2xl font-bold">
                  {stats.length > 0 ? stats[0].modalidade_nome.split(' - ')[0] : '-'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

