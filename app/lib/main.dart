import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';

const bg = Color(0xFF07111F),
    surface = Color(0xFF0E1B2B),
    green = Color(0xFF35E889),
    cyan = Color(0xFF22C7E8),
    muted = Color(0xFF8FA5BC),
    critical = Color(0xFFFF5A65),
    warning = Color(0xFFFFB547);
final apiProvider = Provider((ref) => Api());
final dataProvider = FutureProvider.autoDispose((ref) async {
  final api = ref.read(apiProvider);
  return {
    'stats': await api.get('/api/v1/dashboard/stats'),
    'issues': await api.get('/api/v1/issues'),
    'vehicles': await api.get('/api/v1/vehicles')
  };
});

class Api {
  final Dio dio = Dio(BaseOptions(
      baseUrl: const String.fromEnvironment('API_URL',
          defaultValue: 'http://localhost:8002')));
  Future<dynamic> get(String p) async => (await dio.get(p)).data;
  Future patch(String p, Map<String, dynamic> d) async => dio.patch(p, data: d);
}

void main() => runApp(const ProviderScope(child: CivicEye()));

class CivicEye extends StatelessWidget {
  const CivicEye({super.key});
  @override
  Widget build(c) => MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'CIVIC EYE',
      theme: ThemeData.dark().copyWith(
          scaffoldBackgroundColor: bg,
          colorScheme: const ColorScheme.dark(
              primary: green, secondary: cyan, surface: surface),
          textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
          cardTheme: const CardThemeData(
              color: surface,
              elevation: 0,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.all(Radius.circular(18))))),
      home: const Shell());
}

class Shell extends ConsumerStatefulWidget {
  const Shell({super.key});
  @override
  ConsumerState<Shell> createState() => _ShellState();
}

class _ShellState extends ConsumerState<Shell> {
  int page = 0;
  Timer? timer;
  @override
  void initState() {
    super.initState();
    timer = Timer.periodic(
        const Duration(seconds: 5), (_) => ref.invalidate(dataProvider));
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(c) {
    final wide = MediaQuery.sizeOf(c).width > 850;
    final pages = [
      const Dashboard(),
      const MonitorMap(),
      const Issues(),
      const Analytics(),
      const Settings()
    ];
    final destinations = [
      ('Dashboard', Icons.grid_view_rounded),
      ('Live Map', Icons.map_outlined),
      ('Issues', Icons.warning_amber_rounded),
      ('Analytics', Icons.insights),
      ('Settings', Icons.tune)
    ];
    return Scaffold(
        appBar: wide
            ? null
            : AppBar(backgroundColor: bg, title: const Brand(), actions: [
                const LivePill(),
                IconButton(
                    onPressed: () => ref.invalidate(dataProvider),
                    icon: const Icon(Icons.refresh))
              ]),
        body: Row(children: [
          if (wide)
            Container(
                width: 238,
                color: const Color(0xFF091522),
                padding: const EdgeInsets.fromLTRB(20, 28, 20, 18),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Brand(),
                      const SizedBox(height: 28),
                      const LivePill(),
                      const SizedBox(height: 28),
                      for (var i = 0; i < destinations.length; i++)
                        NavItem(
                            label: destinations[i].$1,
                            icon: destinations[i].$2,
                            selected: i == page,
                            onTap: () => setState(() => page = i)),
                      const Spacer(),
                      const Text('AUTONOMOUS MONITORING',
                          style: TextStyle(
                              color: muted, fontSize: 10, letterSpacing: 1.3)),
                      const SizedBox(height: 8),
                      const Text('No manual capture required',
                          style: TextStyle(color: green, fontSize: 12))
                    ])),
          Expanded(child: pages[page])
        ]),
        bottomNavigationBar: wide
            ? null
            : NavigationBar(
                selectedIndex: page,
                onDestinationSelected: (i) => setState(() => page = i),
                backgroundColor: surface,
                indicatorColor: green.withValues(alpha: .18),
                destinations: [
                    for (final d in destinations)
                      NavigationDestination(icon: Icon(d.$2), label: d.$1)
                  ]));
  }
}

class Brand extends StatelessWidget {
  const Brand({super.key});
  @override
  Widget build(c) => const Row(children: [
        CircleAvatar(
            backgroundColor: green,
            radius: 17,
            child: Icon(Icons.visibility_rounded, color: bg, size: 20)),
        SizedBox(width: 11),
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('CIVIC EYE',
              style:
                  TextStyle(fontWeight: FontWeight.w800, letterSpacing: 1.2)),
          Text('AI OPERATIONS',
              style: TextStyle(color: muted, fontSize: 9, letterSpacing: 1.6))
        ])
      ]);
}

class LivePill extends StatelessWidget {
  const LivePill({super.key});
  @override
  Widget build(c) => Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
          color: green.withValues(alpha: .1),
          borderRadius: BorderRadius.circular(99),
          border: Border.all(color: green.withValues(alpha: .3))),
      child: const Row(mainAxisSize: MainAxisSize.min, children: [
        CircleAvatar(radius: 4, backgroundColor: green),
        SizedBox(width: 7),
        Text('LIVE',
            style: TextStyle(
                color: green, fontWeight: FontWeight.w700, fontSize: 11))
      ]));
}

class NavItem extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;
  const NavItem(
      {super.key,
      required this.label,
      required this.icon,
      required this.selected,
      required this.onTap});
  @override
  Widget build(c) => Padding(
      padding: const EdgeInsets.only(bottom: 7),
      child: ListTile(
          onTap: onTap,
          selected: selected,
          selectedTileColor: green.withValues(alpha: .12),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          leading: Icon(icon, color: selected ? green : muted),
          title: Text(label,
              style: TextStyle(
                  color: selected ? Colors.white : muted,
                  fontWeight: selected ? FontWeight.w700 : FontWeight.w500))));
}

class PageFrame extends StatelessWidget {
  final String title, subtitle;
  final Widget child;
  const PageFrame(
      {super.key,
      required this.title,
      required this.subtitle,
      required this.child});
  @override
  Widget build(c) => SafeArea(
      child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(title,
                style:
                    const TextStyle(fontSize: 29, fontWeight: FontWeight.w800)),
            const SizedBox(height: 5),
            Text(subtitle, style: const TextStyle(color: muted)),
            const SizedBox(height: 24),
            child
          ])));
}

class Dashboard extends ConsumerWidget {
  const Dashboard({super.key});
  @override
  Widget build(c, ref) => PageFrame(
      title: 'Operations Dashboard',
      subtitle: 'Detection → action → independent verification',
      child: ref.watch(dataProvider).when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, s) => ErrorCard('$e'),
          data: (d) {
            final s = d['stats'],
                issues = List<Map<String, dynamic>>.from(d['issues']);
            return Column(children: [
              LayoutBuilder(builder: (c, x) {
                final n = x.maxWidth > 1000
                    ? 5
                    : x.maxWidth > 600
                        ? 3
                        : 2;
                return GridView.count(
                    crossAxisCount: n,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    childAspectRatio: 1.65,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    children: [
                      Metric('ACTIVE', '${s['active_issues']}', green),
                      Metric('NEW', '${s['new']}', cyan),
                      Metric('IN PROGRESS', '${s['in_progress']}', warning),
                      Metric('PENDING VERIFY', '${s['pending_verification']}',
                          const Color(0xFFA78BFA)),
                      Metric('VERIFIED', '${s['verified_resolved']}', green)
                    ]);
              }),
              const SizedBox(height: 20),
              Section(
                  title: 'Latest autonomous detections',
                  child: issues.isEmpty
                      ? const Empty()
                      : Column(children: [
                          for (final i in issues.take(6))
                            IssueTile(
                                i: i, onTap: () => showIssue(c, ref, i['id']))
                        ]))
            ]);
          }));
}

class Metric extends StatelessWidget {
  final String label, value;
  final Color color;
  const Metric(this.label, this.value, this.color, {super.key});
  @override
  Widget build(c) => Card(
      child: Padding(
          padding: const EdgeInsets.all(17),
          child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(label,
                    style: const TextStyle(
                        color: muted, fontSize: 11, letterSpacing: .7)),
                Text(value,
                    style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                        color: color))
              ])));
}

class Section extends StatelessWidget {
  final String title;
  final Widget child;
  const Section({super.key, required this.title, required this.child});
  @override
  Widget build(c) => Card(
      child: Padding(
          padding: const EdgeInsets.all(18),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(title,
                style:
                    const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
            const SizedBox(height: 14),
            child
          ])));
}

class Issues extends ConsumerStatefulWidget {
  const Issues({super.key});
  @override
  ConsumerState<Issues> createState() => _IssuesState();
}

class _IssuesState extends ConsumerState<Issues> {
  String filter = 'ALL';
  @override
  Widget build(c) => PageFrame(
      title: 'Issues',
      subtitle: 'AI-detected observations consolidated by place and time',
      child: ref.watch(dataProvider).when(
          loading: () => const CircularProgressIndicator(),
          error: (e, s) => ErrorCard('$e'),
          data: (d) {
            var rows = List<Map<String, dynamic>>.from(d['issues']);
            if (filter != 'ALL') {
              rows = rows.where((i) => i['issue_type'] == filter).toList();
            }
            return Column(children: [
              Wrap(spacing: 8, children: [
                for (final f in ['ALL', 'WASTE', 'POTHOLE', 'WATERLOGGING'])
                  ChoiceChip(
                      label: Text(f),
                      selected: filter == f,
                      onSelected: (_) => setState(() => filter = f),
                      selectedColor: green.withValues(alpha: .25))
              ]),
              const SizedBox(height: 16),
              Section(
                  title: '${rows.length} consolidated issues',
                  child: rows.isEmpty
                      ? const Empty()
                      : Column(children: [
                          for (final i in rows)
                            IssueTile(
                                i: i, onTap: () => showIssue(c, ref, i['id']))
                        ]))
            ]);
          }));
}

class IssueTile extends StatelessWidget {
  final Map<String, dynamic> i;
  final VoidCallback onTap;
  const IssueTile({super.key, required this.i, required this.onTap});
  Color get color => i['issue_type'] == 'POTHOLE'
      ? critical
      : i['issue_type'] == 'WASTE'
          ? warning
          : cyan;
  @override
  Widget build(c) => InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: Container(
          margin: const EdgeInsets.only(bottom: 9),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
              color: bg.withValues(alpha: .6),
              borderRadius: BorderRadius.circular(14)),
          child: Row(children: [
            Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                    color: color.withValues(alpha: .14),
                    borderRadius: BorderRadius.circular(12)),
                child: Icon(
                    i['issue_type'] == 'POTHOLE'
                        ? Icons.report_problem_outlined
                        : i['issue_type'] == 'WASTE'
                            ? Icons.delete_outline
                            : Icons.water_drop_outlined,
                    color: color)),
            const SizedBox(width: 13),
            Expanded(
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                  Text(i['issue_type'],
                      style: TextStyle(
                          color: color,
                          fontWeight: FontWeight.w800,
                          fontSize: 12)),
                  const SizedBox(height: 4),
                  Text(
                      '${(i['confidence'] ?? i['highest_confidence'] ?? 0) * 100 ~/ 1}% confidence · ${i['detection_count']} detections',
                      style: const TextStyle(color: muted, fontSize: 12))
                ])),
            StatusPill(i['status']),
            const SizedBox(width: 8),
            const Icon(Icons.chevron_right, color: muted)
          ])));
}

class StatusPill extends StatelessWidget {
  final String value;
  const StatusPill(this.value, {super.key});
  @override
  Widget build(c) => Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
      decoration: BoxDecoration(
          color: green.withValues(alpha: .1),
          borderRadius: BorderRadius.circular(8)),
      child: Text(value.replaceAll('_', ' '),
          style: const TextStyle(
              color: green, fontSize: 9, fontWeight: FontWeight.w700)));
}

class MonitorMap extends ConsumerWidget {
  const MonitorMap({super.key});
  @override
  Widget build(c, ref) => PageFrame(
      title: 'Live Monitoring Map',
      subtitle: 'Automatic detections and vehicle verification coverage',
      child: SizedBox(
          height: 620,
          child: Stack(children: [
            Container(
                decoration: BoxDecoration(
                    color: surface,
                    borderRadius: BorderRadius.circular(22),
                    image: const DecorationImage(
                        image: NetworkImage(
                            'https://tile.openstreetmap.org/12/2934/1874.png'),
                        fit: BoxFit.cover,
                        opacity: .38))),
            ref.watch(dataProvider).when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, s) => const SizedBox(),
                data: (d) {
                  final issues = List<Map<String, dynamic>>.from(d['issues']);
                  return Stack(children: [
                    for (var x = 0; x < issues.length; x++)
                      Positioned(
                          left: 70.0 + (x * 137) % 600,
                          top: 90.0 + (x * 91) % 400,
                          child: Tooltip(
                              message: issues[x]['issue_type'],
                              child: const CircleAvatar(
                                  backgroundColor: green,
                                  radius: 18,
                                  child: Icon(Icons.location_on,
                                      color: bg, size: 20))))
                  ]);
                }),
            const Positioned(left: 18, top: 18, child: LivePill()),
            const Positioned(
                left: 18,
                bottom: 18,
                child: Card(
                    child: Padding(
                        padding: EdgeInsets.all(12),
                        child: Text(
                            'MapLibre-ready · configurable tiles\nMarkers update every 5 seconds',
                            style: TextStyle(color: muted, fontSize: 11)))))
          ])));
}

class Analytics extends ConsumerWidget {
  const Analytics({super.key});
  @override
  Widget build(c, ref) => PageFrame(
      title: 'Analytics',
      subtitle: 'Operational outcomes from autonomous evidence',
      child: ref.watch(dataProvider).when(
          loading: () => const CircularProgressIndicator(),
          error: (e, s) => ErrorCard('$e'),
          data: (d) {
            final s = d['stats'];
            return Column(children: [
              LayoutBuilder(
                  builder: (c, x) => GridView.count(
                          crossAxisCount: x.maxWidth > 700 ? 4 : 2,
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          crossAxisSpacing: 12,
                          mainAxisSpacing: 12,
                          childAspectRatio: 1.5,
                          children: [
                            Metric(
                                'DETECTIONS', '${s['total_detections']}', cyan),
                            Metric('ACTIVE', '${s['active_issues']}', warning),
                            Metric(
                                'RESOLVED', '${s['verified_resolved']}', green),
                            Metric(
                                'VERIFY RATE',
                                s['active_issues'] + s['verified_resolved'] == 0
                                    ? '0%'
                                    : '${(100 * s['verified_resolved'] / (s['active_issues'] + s['verified_resolved'])).round()}%',
                                green)
                          ])),
              const SizedBox(height: 16),
              Section(
                  title: 'Issues by type',
                  child: Column(children: [
                    for (final e in (s['by_type'] as Map).entries)
                      Padding(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          child: Row(children: [
                            SizedBox(width: 120, child: Text(e.key)),
                            Expanded(
                                child: LinearProgressIndicator(
                                    value: (e.value as int) /
                                        (s['active_issues'] == 0
                                            ? 1
                                            : s['active_issues']),
                                    minHeight: 9,
                                    borderRadius: BorderRadius.circular(9))),
                            const SizedBox(width: 12),
                            Text('${e.value}')
                          ]))
                  ]))
            ]);
          }));
}

class Settings extends StatelessWidget {
  const Settings({super.key});
  @override
  Widget build(c) => PageFrame(
      title: 'System',
      subtitle: 'Edge fleet and platform configuration',
      child: Column(children: [
        Section(
            title: 'Autonomous monitoring',
            child: Column(children: [
              config(Icons.videocam_outlined, 'Camera pipeline',
                  'Continuous capture · no manual controls', true),
              config(Icons.psychology_outlined, 'Local AI inference',
                  'YOLO-compatible checkpoint · no cloud AI keys', true),
              config(Icons.cloud_off_outlined, 'Offline queue',
                  'SQLite evidence retention and retry', true),
              config(Icons.verified_outlined, 'Independent verification',
                  'Second-vehicle recheck enabled', true)
            ])),
        const SizedBox(height: 14),
        Section(
            title: 'Platform',
            child: Column(children: [
              config(Icons.storage, 'Evidence storage',
                  'Local filesystem abstraction', false),
              config(Icons.map_outlined, 'Map tiles',
                  'Configurable MapLibre tile URL', false)
            ]))
      ]));
  Widget config(IconData icon, String title, String text, bool ok) => ListTile(
      leading: Icon(icon, color: ok ? green : cyan),
      title: Text(title),
      subtitle: Text(text, style: const TextStyle(color: muted)),
      trailing: ok
          ? const Icon(Icons.check_circle, color: green)
          : const Icon(Icons.chevron_right));
}

class Empty extends StatelessWidget {
  const Empty({super.key});
  @override
  Widget build(c) => const Padding(
      padding: EdgeInsets.all(35),
      child: Column(children: [
        Icon(Icons.radar, color: green, size: 42),
        SizedBox(height: 12),
        Text('Awaiting autonomous detections'),
        SizedBox(height: 5),
        Text('Start an edge camera to populate this view.',
            style: TextStyle(color: muted))
      ]));
}

class ErrorCard extends StatelessWidget {
  final String e;
  const ErrorCard(this.e, {super.key});
  @override
  Widget build(c) => Card(
      child: Padding(
          padding: const EdgeInsets.all(20),
          child: Text('Backend unavailable\n$e',
              style: const TextStyle(color: critical))));
}

Future showIssue(BuildContext c, WidgetRef ref, String id) async {
  final api = ref.read(apiProvider);
  final i = await api.get('/api/v1/issues/$id');
  if (!c.mounted) return;
  showModalBottomSheet(
      context: c,
      isScrollControlled: true,
      backgroundColor: surface,
      builder: (context) => IssueDetail(
          i: i, api: api, onChanged: () => ref.invalidate(dataProvider)));
}

class IssueDetail extends StatefulWidget {
  final Map<String, dynamic> i;
  final Api api;
  final VoidCallback onChanged;
  const IssueDetail(
      {super.key, required this.i, required this.api, required this.onChanged});
  @override
  State<IssueDetail> createState() => _IssueDetailState();
}

class _IssueDetailState extends State<IssueDetail> {
  bool busy = false;
  Future go(String status) async {
    setState(() => busy = true);
    try {
      await widget.api.patch('/api/v1/issues/${widget.i['id']}', {
        'status': status,
        if (status == 'ASSIGNED') 'assigned_department': 'Road Operations'
      });
      widget.onChanged();
      if (mounted) Navigator.pop(context);
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(c) {
    final i = widget.i,
        events = List<Map<String, dynamic>>.from(i['events'] ?? []),
        status = i['status'];
    final action = status == 'NEW'
        ? 'ASSIGNED'
        : status == 'ASSIGNED'
            ? 'IN_PROGRESS'
            : status == 'IN_PROGRESS'
                ? 'PENDING_VERIFICATION'
                : null;
    return SafeArea(
        child: DraggableScrollableSheet(
            expand: false,
            initialChildSize: .86,
            maxChildSize: .95,
            builder: (c, scroll) => SingleChildScrollView(
                controller: scroll,
                padding: const EdgeInsets.all(24),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(children: [
                        Expanded(
                            child: Text(i['issue_type'],
                                style: const TextStyle(
                                    fontSize: 26,
                                    fontWeight: FontWeight.w800))),
                        StatusPill(status),
                        IconButton(
                            onPressed: () => Navigator.pop(c),
                            icon: const Icon(Icons.close))
                      ]),
                      Text('Issue ${i['id']}',
                          style: const TextStyle(color: muted, fontSize: 11)),
                      const SizedBox(height: 18),
                      if (events.isNotEmpty)
                        ClipRRect(
                            borderRadius: BorderRadius.circular(16),
                            child: Image.network(
                                '${widget.api.dio.options.baseUrl}${events.first['image_url']}',
                                height: 220,
                                width: double.infinity,
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) => Container(
                                    height: 180,
                                    color: bg,
                                    child: const Center(
                                        child: Icon(
                                            Icons.image_not_supported_outlined,
                                            color: muted))))),
                      const SizedBox(height: 18),
                      Wrap(spacing: 10, runSpacing: 10, children: [
                        MetricMini('CONFIDENCE',
                            '${(i['highest_confidence'] * 100).round()}%'),
                        MetricMini('SEVERITY', i['severity']),
                        MetricMini('DETECTIONS', '${i['detection_count']}'),
                        MetricMini('STATUS', status.replaceAll('_', ' '))
                      ]),
                      const SizedBox(height: 18),
                      Section(
                          title: 'Location & evidence',
                          child: Column(children: [
                            ListTile(
                                leading:
                                    const Icon(Icons.location_on, color: cyan),
                                title:
                                    Text('${i['latitude']}, ${i['longitude']}'),
                                subtitle: const Text(
                                    'GPS attached automatically',
                                    style: TextStyle(color: muted))),
                            for (final e in events)
                              ListTile(
                                  leading:
                                      const Icon(Icons.videocam, color: green),
                                  title: Text('Detected by ${e['vehicle_id']}'),
                                  subtitle: Text(
                                      '${e['captured_at']} · ${(e['confidence'] * 100).round()}% confidence',
                                      style: const TextStyle(color: muted)))
                          ])),
                      const SizedBox(height: 14),
                      if (action != null)
                        SizedBox(
                            width: double.infinity,
                            child: FilledButton.icon(
                                onPressed: busy ? null : () => go(action),
                                icon: Icon(action == 'PENDING_VERIFICATION'
                                    ? Icons.verified_outlined
                                    : Icons.arrow_forward),
                                label: Padding(
                                    padding: const EdgeInsets.all(14),
                                    child: Text(action == 'PENDING_VERIFICATION'
                                        ? 'MARK WORK COMPLETE → PENDING VERIFICATION'
                                        : action.replaceAll('_', ' '))))),
                      if (status == 'PENDING_VERIFICATION')
                        const Card(
                            child: Padding(
                                padding: EdgeInsets.all(18),
                                child: Row(children: [
                                  Icon(Icons.radar, color: green),
                                  SizedBox(width: 12),
                                  Expanded(
                                      child: Text(
                                          'Awaiting an independent vehicle pass. Resolution cannot be self-certified.'))
                                ])))
                    ]))));
  }
}

class MetricMini extends StatelessWidget {
  final String a, b;
  const MetricMini(this.a, this.b, {super.key});
  @override
  Widget build(c) => Container(
      width: 150,
      padding: const EdgeInsets.all(13),
      decoration:
          BoxDecoration(color: bg, borderRadius: BorderRadius.circular(12)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(a, style: const TextStyle(color: muted, fontSize: 9)),
        const SizedBox(height: 5),
        Text(b, style: const TextStyle(fontWeight: FontWeight.w700))
      ]));
}
